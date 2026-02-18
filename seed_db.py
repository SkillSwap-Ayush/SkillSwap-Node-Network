import sqlite3
import hashlib

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def seed():
    # Database connection
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    print("Cleaning old data...")
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('DROP TABLE IF EXISTS skills')
    
    # Tables banana
    cursor.execute('''CREATE TABLE users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT NOT NULL, 
                    email UNIQUE NOT NULL, 
                    password TEXT NOT NULL,
                    bio TEXT DEFAULT 'Member',
                    role TEXT DEFAULT 'User',
                    location TEXT DEFAULT 'Not Set',
                    website TEXT DEFAULT '',
                    is_admin INTEGER DEFAULT 0)''')
    
    cursor.execute('''CREATE TABLE skills 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id INTEGER, 
                    skill_name TEXT NOT NULL, 
                    skill_type TEXT NOT NULL, 
                    FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Users Data (Dhyan rakhna columns counts match karein)
    # Name, Email, Password, Bio, Role, Location, Website, Is_Admin
    users = [
        ('Ayush Admin', 'admin@skillswap.com', hash_pass('admin123'), 'Network Boss', 'Admin', 'Control Center', 'www.admin.com', 1),
        ('Amit Sharma', 'amit@skillswap.com', hash_pass('123'), 'Python Expert', 'Mentor', 'Mumbai', '', 0),
        ('Sneha Designer', 'sneha@skillswap.com', hash_pass('123'), 'UI Expert', 'Mentor', 'Delhi', '', 0)
    ]

    cursor.executemany('INSERT INTO users (name, email, password, bio, role, location, website, is_admin) VALUES (?,?,?,?,?,?,?,?)', users)
    conn.commit()

    # IDs fetch karna skills add karne ke liye
    cursor.execute('SELECT id FROM users WHERE email="amit@skillswap.com"')
    amit_id = cursor.fetchone()[0]
    cursor.execute('SELECT id FROM users WHERE email="sneha@skillswap.com"')
    sneha_id = cursor.fetchone()[0]

    skills = [
        (amit_id, 'Programming', 'Teach'),
        (amit_id, 'Python', 'Teach'),
        (sneha_id, 'UI/UX Design', 'Teach'),
        (sneha_id, 'Figma', 'Teach')
    ]
    cursor.executemany('INSERT INTO skills (user_id, skill_name, skill_type) VALUES (?,?,?)', skills)
    
    conn.commit()
    conn.close()
    print("🚀 SUCCESS: Database Seeded!")
    print("Admin: admin@skillswap.com | Pass: admin123")

if __name__ == '__main__':
    seed()