from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import sqlite3
import os
import secrets


admission_bp = Blueprint('admission_bp', __name__)


# ========= Configuration / Utilities =========
DATABASE = 'users.db'

def get_db():
    return sqlite3.connect(DATABASE)

def generate_complex_password(length: int = 12) -> str:
    return secrets.token_urlsafe(max(8, length))[:length]

def generate_admission_username(admission_id: int, student_name: str) -> str:
    base = (student_name or '').strip().lower().replace(' ', '')
    return f"ADM{admission_id:06d}" if not base else f"ADM{admission_id:06d}"


# ========= Student-Facing Endpoints =========
@admission_bp.route('/admission', methods=['GET', 'POST'])
def admission_form():
    if request.method == 'GET':
        return render_template('admission.html')

    # Validate fields
    required = ['student_name','dob','student_phone','student_email','class','school_name','maths_marks','maths_rating','last_percentage','parent_name','parent_phone']
    for f in required:
        if not request.form.get(f):
            flash(f"Missing required field: {f}", 'error')
            return redirect(url_for('admission_bp.admission_form'))

    # Photo
    photo = request.files.get('passport_photo')
    if not photo or photo.filename == '':
        flash('Passport photo is required.', 'error')
        return redirect(url_for('admission_bp.admission_form'))
    if not ('.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() in {'png','jpg','jpeg'}):
        flash('Invalid photo format. Only PNG, JPG, JPEG allowed.', 'error')
        return redirect(url_for('admission_bp.admission_form'))
    filename = secure_filename(photo.filename)
    unique_name = secrets.token_hex(8) + '_' + filename
    photo_path = os.path.join('uploads', 'admission_photos', unique_name)
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
    photo.save(photo_path)

    # Insert admission
    conn = get_db()
    c = conn.cursor()

    class_name = request.form['class']
    class_mappings = {'9': 'class 9','10': 'class 10','11': 'class 11 applied','12': 'class 12 applied'}
    normalized_class = class_mappings.get((class_name or '').lower(), class_name)

    c.execute('''INSERT INTO admissions (
        student_name, dob, student_phone, student_email, class, school_name,
        maths_marks, maths_rating, last_percentage, parent_name, parent_phone,
        passport_photo, status, submitted_at, user_id, submit_ip
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        request.form['student_name'], request.form['dob'], request.form['student_phone'],
        request.form['student_email'], normalized_class, request.form['school_name'],
        request.form['maths_marks'], request.form['maths_rating'], request.form['last_percentage'],
        request.form['parent_name'], request.form['parent_phone'], unique_name, 'pending',
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'), session.get('user_id'),
        ((request.headers.get('X-Forwarded-For','').split(',')[0].strip()) or request.remote_addr or 'unknown')
    ))
    new_id = c.lastrowid

    # Credentials
    admission_username = generate_admission_username(new_id, request.form['student_name'])
    access_password = generate_complex_password(12)
    hashed_pw = generate_password_hash(access_password)
    c.execute('''INSERT OR IGNORE INTO admission_access (admission_id, access_username, access_password)
                 VALUES (?, ?, ?)''', (new_id, admission_username, hashed_pw))
    c.execute('''CREATE TABLE IF NOT EXISTS admission_access_plain (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admission_id INTEGER NOT NULL UNIQUE,
        access_username TEXT UNIQUE,
        access_password_plain TEXT NOT NULL,
        login_username TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    login_username = (request.form['student_name'] or '').strip().lower().replace(' ', '')
    c.execute('''INSERT OR REPLACE INTO admission_access_plain (admission_id, access_username, access_password_plain, login_username)
                 VALUES (?, ?, ?, ?)''', (new_id, admission_username, access_password, login_username))
    conn.commit()
    conn.close()

    session['last_admission_creds'] = {
        'admission_username': admission_username,
        'password': access_password,
        'login_username': login_username,
    }

    student = {
        'student_name': request.form['student_name'],
        'dob': request.form['dob'],
        'student_phone': request.form['student_phone'],
        'student_email': request.form['student_email'],
        'class': normalized_class,
        'school_name': request.form['school_name'],
        'maths_marks': request.form['maths_marks'],
        'maths_rating': request.form['maths_rating'],
        'last_percentage': request.form['last_percentage'],
        'parent_name': request.form['parent_name'],
        'parent_phone': request.form['parent_phone'],
        'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    creds = session.get('last_admission_creds')
    return render_template('admission_success.html', student=student, creds=creds)


@admission_bp.route('/check-admission', methods=['GET', 'POST'])
def check_admission():
    if request.method == 'POST':
        access_username = request.form.get('access_username')
        access_password = request.form.get('access_password')
        if not access_username or not access_password:
            flash('Please provide both username and password', 'error')
            return render_template('check_admission_login.html')
        result = _check_admission_by_credentials(access_username, access_password)
        if result:
            return render_template('check_admission_login.html', result=True,
                                   status=result.get('status'), paid_status=result.get('paid_status'),
                                   details=result.get('details'), access_username=access_username,
                                   access_password=access_password)
        flash('Invalid credentials. Please check your username and password.', 'error')
        return render_template('check_admission_login.html', access_username=access_username)

    last_creds = session.pop('last_admission_creds', None)
    if last_creds:
        return render_template('check_admission_login.html', from_submission=True,
                               access_username=last_creds.get('admission_username'),
                               access_password=last_creds.get('password'))
    return render_template('check_admission_login.html')





# ========= Internal: credential check =========
def _check_admission_by_credentials(access_username: str, access_password: str):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('SELECT admission_id, access_password FROM admission_access WHERE access_username=?', (access_username,))
        row = c.fetchone()
        admission_id = None
        if row:
            possible, hashed_pw = row
            try:
                if check_password_hash(hashed_pw, access_password):
                    admission_id = possible
            except Exception:
                admission_id = None

        if not admission_id:
            try:
                c.execute('SELECT admission_id FROM admission_access_plain WHERE access_username=? AND access_password_plain=?', (access_username, access_password))
                plain = c.fetchone()
            except sqlite3.OperationalError:
                c.execute('SELECT admission_id FROM admission_access_plain WHERE access_username=? AND plain_password=?', (access_username, access_password))
                plain = c.fetchone()
            if plain:
                admission_id = plain[0]

        if not admission_id:
            conn.close()
            return None

        # pending
        c.execute('SELECT student_name, class, school_name, status, submitted_at FROM admissions WHERE id=?', (admission_id,))
        adm = c.fetchone()
        if adm:
            conn.close()
            return {'status': adm[3], 'paid_status': 'unpaid', 'details': {'student_name': adm[0], 'class': adm[1], 'school_name': adm[2], 'submitted_at': adm[4]}}

        # approved
        c.execute('SELECT student_name, class, school_name, approved_at FROM approved_admissions WHERE original_admission_id=?', (admission_id,))
        adm = c.fetchone()
        if adm:
            conn.close()
            return {'status': 'approved', 'paid_status': 'unpaid', 'details': {'student_name': adm[0], 'class': adm[1], 'school_name': adm[2], 'submitted_at': adm[3]}}

        # disapproved
        c.execute('SELECT student_name, class, school_name, disapproved_at FROM disapproved_admissions WHERE original_admission_id=?', (admission_id,))
        adm = c.fetchone()
        if adm:
            conn.close()
            return {'status': 'disapproved', 'paid_status': 'unpaid', 'details': {'student_name': adm[0], 'class': adm[1], 'school_name': adm[2], 'submitted_at': adm[3]}}

        conn.close()
        return None
    except Exception as e:
        print('[admission_bp] credential check error:', e)
        conn.close()
        return None


