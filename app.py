from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import random
import hashlib

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'ayush_rtx3090_secret_key_pro'

# --- DATABASE PATH CONFIGURATION (Render Special) ---
basedir = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(basedir, 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- MODULES / UTILS ---
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = get_db_connection()
    # Users Table
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT NOT NULL, 
                    email UNIQUE NOT NULL, 
                    password TEXT NOT NULL,
                    bio TEXT DEFAULT 'SkillSwap Node Member',
                    role TEXT DEFAULT 'Expert/Mentor',
                    location TEXT DEFAULT 'Not Set',
                    website TEXT DEFAULT '',
                    is_admin INTEGER DEFAULT 0)''')
    
    # Skills Table
    conn.execute('''CREATE TABLE IF NOT EXISTS skills 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_id INTEGER, 
                    skill_name TEXT NOT NULL, 
                    skill_type TEXT NOT NULL, 
                    FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

with app.app_context():
    init_db()

# --- AUTH ROUTES ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_pass(request.form['password'])
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        flash('Invalid Credentials!', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_pass(request.form['password'])
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (name, email, password, is_admin) VALUES (?, ?, ?, 0)', (name, email, password))
            conn.commit()
            flash('Account Created! Please Login.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Email already exists!', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

# --- MAIN DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    selected_cat = request.args.get('category', 'All')
    conn = get_db_connection()
    
    db_stats = conn.execute('''SELECT 
        (SELECT COUNT(*) FROM users) as total_users, 
        (SELECT COUNT(*) FROM skills WHERE skill_type="Teach") as total_mentors, 
        (SELECT COUNT(*) FROM skills) as total_skills
    ''').fetchone()

    analytics = {
        'match_accuracy': f"{random.randint(88, 99)}%",
        'community_growth': f"+{random.randint(12, 30)}%",
        'ai_recommendations': ['React Pro', 'UI/UX Design', 'Cloud Architecture', 'Python AI'],
        'node_status': 'Ultra-Stable',
        'reputation_score': random.randint(450, 999)
    }

    telemetry = {
        'uptime': '99.99%', 
        'node_load': f"{random.randint(8, 22)}%", 
        'active_swaps': random.randint(1200, 4500),
        'server_region': 'India-West-1'
    }
    
    if selected_cat == 'All':
        others = conn.execute('''SELECT users.name, skills.skill_name, skills.skill_type 
                                 FROM users JOIN skills ON users.id = skills.user_id 
                                 WHERE users.id != ? LIMIT 15''', (session['user_id'],)).fetchall()
    else:
        others = conn.execute('''SELECT users.name, skills.skill_name, skills.skill_type 
                                 FROM users JOIN skills ON users.id = skills.user_id 
                                 WHERE users.id != ? AND (skills.skill_name LIKE ? OR skills.skill_name LIKE ?)''', 
                              (session['user_id'], f'%{selected_cat}%', f'%{selected_cat}%')).fetchall()
    
    my_skills = conn.execute('SELECT * FROM skills WHERE user_id = ?', (session['user_id'],)).fetchall()
    all_users = conn.execute('SELECT * FROM users').fetchall() if session.get('is_admin') == 1 else []
    conn.close()
    
    return render_template('dashboard.html', 
                           name=session['user_name'], 
                           stats=db_stats, 
                           analytics=analytics, 
                           telemetry=telemetry, 
                           others=others, 
                           my_skills=my_skills, 
                           current_cat=selected_cat,
                           all_users=all_users)

# --- SKILL MANAGEMENT ---
@app.route('/add_skill', methods=['POST'])
def add_skill():
    if 'user_id' not in session: return redirect(url_for('login'))
    name = request.form.get('skill_name')
    skill_type = request.form.get('skill_type')
    if name:
        conn = get_db_connection()
        conn.execute('INSERT INTO skills (user_id, skill_name, skill_type) VALUES (?, ?, ?)', 
                     (session['user_id'], name, skill_type))
        conn.commit()
        conn.close()
        flash(f'Skill {name} added to your node!', 'success')
    return redirect(url_for('dashboard'))

# --- USER PROFILE ---
@app.route('/profile')
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    user_skills = conn.execute('SELECT * FROM skills WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('profile.html', name=session['user_name'], user=user_data, user_skills=user_skills)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('UPDATE users SET name = ?, bio = ?, role = ?, location = ?, website = ? WHERE id = ?', 
                 (request.form.get('full_name'), request.form.get('bio'), request.form.get('role'), request.form.get('location'), request.form.get('website'), session['user_id']))
    conn.commit()
    conn.close()
    session['user_name'] = request.form.get('full_name')
    flash('Node Profile Updated!', 'success')
    return redirect(url_for('profile'))

# --- FEATURES ---
@app.route('/notifications')
def notifications():
    if 'user_id' not in session: return redirect(url_for('login'))
    notifs = [
        {'id': 1, 'title': 'Skill Match!', 'desc': 'New Mentor found for Python.', 'time': '2m ago', 'icon': 'bi-lightning', 'color': 'info'},
        {'id': 2, 'title': 'System Update', 'desc': 'Node RTX 3090 optimized.', 'time': '1h ago', 'icon': 'bi-cpu', 'color': 'primary'}
    ]
    return render_template('notifications.html', name=session['user_name'], notifications=notifs)

@app.route('/settings')
def settings():
    if 'user_id' not in session: return redirect(url_for('login'))
    options = {
        'privacy': ['Public Node', 'Show Email', 'Allow Direct Swaps'],
        'alerts': ['Email Pings', 'Match Notifications', 'Node Reports']
    }
    return render_template('settings.html', name=session['user_name'], options=options)

@app.route('/mentors')
def mentors():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    mentors_list = conn.execute('''SELECT users.name, skills.skill_name, users.email 
                                 FROM users JOIN skills ON users.id = skills.user_id 
                                 WHERE skills.skill_type = "Teach"''').fetchall()
    conn.close()
    return render_template('mentors.html', name=session['user_name'], mentors=mentors_list)

@app.route('/categories')
def categories():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('categories.html', name=session['user_name'])

@app.route('/help')
def help():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('help.html', name=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ADMIN PURGE ---
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('is_admin') == 1:
        conn = get_db_connection()
        conn.execute('DELETE FROM skills WHERE user_id = ?', (user_id,))
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        flash(f"User #{user_id} removed!", "warning")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)