from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from models import db, User, Post # Import db from models

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gizli-anahtar-varsayilan-local')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Initialize db with app
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models after db initialization to avoid circular import
from models import db, User, Post, Comment, Project, Skill

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).limit(6).all()
    # Skills grouped by category (or handled in template)
    skills = Skill.query.all()
    # Projects filterable by category
    projects = Project.query.order_by(Project.date_created.desc()).all()
    
    # Simple grouping for easier template rendering if needed, 
    # but for now we pass all and let template filter
    return render_template('index.html', posts=posts, skills=skills, projects=projects)

@app.route('/blog')
def blog():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('blog.html', posts=posts)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        username = request.form.get('username')
        content = request.form.get('content')
        comment = Comment(username=username, content=content, post=post)
        db.session.add(comment)
        db.session.commit()
        flash('Yorumunuz gönderildi!')
        return redirect(url_for('post', post_id=post.id))
    return render_template('post.html', post=post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'): # Not hashing for simplicity as requested, but should use hashing in prod
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Giriş başarısız. Lütfen bilgilerinizi kontrol edin.')
            
    return render_template('login.html')

from werkzeug.utils import secure_filename

app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yapıldı.')
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        image_url = request.form.get('image_file')
        file = request.files.get('file')
        
        final_image = None
        
        # Dosya yükleme kontrolü
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Klasörün var olduğundan emin ol
            os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
            file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            final_image = url_for('static', filename='uploads/' + filename)
        elif image_url:
            final_image = image_url
        
        post = Post(title=title, content=content, image_file=final_image)
        db.session.add(post)
        db.session.commit()
        flash('Yazı başarıyla paylaşıldı!')
        return redirect(url_for('admin'))
        
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    projects = Project.query.all()
    skills = Skill.query.all()
    return render_template('admin.html', posts=posts, projects=projects, skills=skills)

@app.route('/delete/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Yazı silindi.')
    return redirect(url_for('admin'))

@app.route('/admin/project', methods=['POST'])
@login_required
def add_project():
    title = request.form.get('title')
    description = request.form.get('description')
    link = request.form.get('link')
    github_link = request.form.get('github_link')
    category = request.form.get('category')
    tags = request.form.get('tags')
    
    # Image handling removed as per user request
    # final_image = 'default_project.jpg'

    project = Project(title=title, description=description, link=link, github_link=github_link, category=category, tags=tags)
    db.session.add(project)
    db.session.commit()
    flash('Proje eklendi!')
    return redirect(url_for('admin'))

@app.route('/admin/project/delete/<int:id>')
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    flash('Proje silindi.')
    return redirect(url_for('admin'))

@app.route('/admin/skill', methods=['POST'])
@login_required
def add_skill():
    name = request.form.get('name')
    icon = request.form.get('icon')
    category = request.form.get('category')
    
    skill = Skill(name=name, icon=icon, category=category)
    db.session.add(skill)
    db.session.commit()
    flash('Yetenek eklendi!')
    return redirect(url_for('admin'))

@app.route('/admin/skill/delete/<int:id>')
@login_required
def delete_skill(id):
    skill = Skill.query.get_or_404(id)
    db.session.delete(skill)
    db.session.commit()
    flash('Yetenek silindi.')
    return redirect(url_for('admin'))

# Admin kullanıcısını oluşturmak için geçici route
@app.route('/create_admin')
def create_admin():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        user = User(username='admin', password='password123') # Basit şifre
        db.session.add(user)
        db.session.commit()
        return "Admin kullanıcısı oluşturuldu! (Kullanıcı: admin, Şifre: password123)"
    return "Admin zaten mevcut."



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
