from app import app, db
from models import Project, Skill

def seed_data():
    with app.app_context():
        db.create_all()
        
        # Check if data already exists to avoid duplicates (optional, but good practice)
        if Project.query.first() or Skill.query.first():
            print("Veritabanı zaten dolu, ekleme yapılmadı.")
            # Optional: db.drop_all(); db.create_all() to force fresh start
            # but usually safer to just return or delete specific items
            # For this task, let's assume we want to FRESH start for projects/skills
            Project.query.delete()
            Skill.query.delete()
            db.session.commit()
            print("Eski veriler temizlendi.")

        # --- Skills ---
        skills = [
            # Frontend
            Skill(name='HTML/CSS', icon='fab fa-html5', category='Frontend'),
            Skill(name='Javascript', icon='fab fa-js', category='Frontend'),
            Skill(name='React', icon='fab fa-react', category='Frontend'),
            Skill(name='UI/UX Design', icon='fas fa-palette', category='Frontend'),
            
            # Backend
            Skill(name='Python', icon='fab fa-python', category='Backend'),
            Skill(name='MySQL', icon='fas fa-database', category='Backend'),
            Skill(name='MongoDB', icon='fas fa-leaf', category='Backend'),
            
            # Languages
            Skill(name='Java', icon='fab fa-java', category='Languages'),
            Skill(name='C', icon='fas fa-microchip', category='Languages'),
            Skill(name='C#', icon='fas fa-code', category='Languages'),
            Skill(name='C++', icon='fas fa-terminal', category='Languages'),
            
            # Game
            Skill(name='Unity', icon='fab fa-unity', category='Game'),
            Skill(name='Game Design', icon='fas fa-gamepad', category='Game'),
        ]
        
        db.session.add_all(skills)
        
        # --- Projects from User Request ---
        projects = [
            Project(
                title='To-Do App',
                description='Kullanıcıların günlük görevlerini ekleyip, tamamlayıp silebildiği pratik bir görev yönetim uygulaması.',
                category='web',
                tags='HTML, CSS, JS, LocalStorage',
                github_link='https://github.com/nazimisenc'
            ),
            Project(
                title='Kim Milyoner Olmak İster',
                description='Televizyon yarışması formatında, süre ve joker özellikli bilgi yarışması oyunu.',
                category='game', # or web
                tags='C#, Unity, Educational',
                github_link='https://github.com/nazimisenc'
            ),
            Project(
                title='Alışveriş Sitesi',
                description='Ürün listeleme, sepet yönetimi ve ödeme simülasyonu içeren kapsamlı e-ticaret platformu.',
                category='web',
                tags='Python, Flask, SQLite, Bootstrap',
                github_link='https://github.com/nazimisenc'
            ),
             Project(
                title='Profil Blog',
                description='Kişisel blog yazılarının paylaşıldığı, dinamik içerik yönetimine sahip portfolyo sitesi.',
                category='web',
                tags='Python, Flask, Admin Panel',
                github_link='https://github.com/nazimisenc'
            ),
        ]
        
        db.session.add_all(projects)
        db.session.commit()
        print("Veritabanı başarıyla güncellendi (Seed Data).")

if __name__ == '__main__':
    seed_data()
