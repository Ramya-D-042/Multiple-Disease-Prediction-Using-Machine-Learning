from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3, os, joblib, numpy as np, random, smtplib
from werkzeug.security import generate_password_hash, check_password_hash

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, 'database.db')
MODELS_DIR = os.path.join(APP_DIR, 'models')

app = Flask(__name__)
app.secret_key = 'change_this_secret_key'  # change in production

# -------------------------
# OTP / Email Config
# -------------------------
EMAIL_ADDRESS = 'nischithaup35@gmail.com'  # your Gmail
EMAIL_PASSWORD = 'hlsldvgiaxxzhlsj'       # Gmail app password (use env vars in prod)
otp_store = {}

# -------------------------
# Ensure models dir exists
# -------------------------
if not os.path.exists(MODELS_DIR):
    os.makedirs(MODELS_DIR, exist_ok=True)

# -------------------------
# Initialize DB
# -------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT,
        phone TEXT,
        password TEXT
    )''')
    conn.commit()
    conn.close()
init_db()

# -------------------------
# Load models
# -------------------------
unified_models = {}
unified_scaler = None
try:
    heart_path = os.path.join(MODELS_DIR,'unified_heart.pkl')
    diab_path = os.path.join(MODELS_DIR,'unified_diabetes.pkl')
    park_path = os.path.join(MODELS_DIR,'unified_parkinsons.pkl')
    scaler_path = os.path.join(MODELS_DIR,'unified_scaler.pkl')

    if os.path.exists(heart_path):
        unified_models['heart'] = joblib.load(heart_path)
    if os.path.exists(diab_path):
        unified_models['diabetes'] = joblib.load(diab_path)
    if os.path.exists(park_path):
        unified_models['parkinsons'] = joblib.load(park_path)
    if os.path.exists(scaler_path):
        unified_scaler = joblib.load(scaler_path)

    if not unified_models:
        print("Warning: No unified models found in", MODELS_DIR)
    else:
        print("Loaded models:", list(unified_models.keys()))
    if unified_scaler is None:
        print("No unified_scaler loaded (it's optional).")
except Exception as e:
    print('Error loading models:', e)

# -------------------------
# DB helper
# -------------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------------
# Simple home route (avoid missing template errors)
# -------------------------
@app.route('/home')
@app.route('/index')
def home():
    # If you have a home.html, change this to `return render_template('home.html')`
    # For now redirect to login to be safe
    return redirect(url_for('login'))

# -------------------------
# Contact info
# -------------------------
@app.route('/contact_info')
def contact_info():
    return jsonify({
        'contacts': [
            {'email':'dramya885@gmail.com', 'phone':'6360677285'},
            {'email':'preethiraj241@gmail.com', 'phone':'8951307665'}
        ]
    })

# -------------------------
# Admin view users (requires admin session)
# -------------------------
@app.route('/admin/users')
def admin_users():
    # Use session['admin'] to check admin privileges
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db(); cur = conn.cursor()
    cur.execute('SELECT id, username, email, phone FROM users')
    rows = cur.fetchall(); conn.close()
    return render_template('admin_users.html', users=rows)

# -------------------------
# User Login / Signup
# -------------------------
@app.route('/login', methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        conn = get_db(); cur = conn.cursor()
        # Check by username OR email
        cur.execute('SELECT username, password FROM users WHERE username=? OR email=?', 
                    (username_or_email, username_or_email))
        row = cur.fetchone(); conn.close()
        if row and check_password_hash(row['password'], password):
            # if the account actually is the admin user, force admin login flow
            if row['username'] == 'admin':
                flash('Use Admin Login form for admin','danger')
                return redirect(url_for('admin_login'))
            session['user'] = row['username']
            return redirect(url_for('predict'))
        flash('Invalid username/email or password','danger')
    return render_template('login.html', require_email=False)

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username = request.form.get('username','').strip()
        email = request.form.get('email','').strip()
        phone = request.form.get('phone','').strip()
        password = request.form.get('password','').strip()
        import re
        if len(password)<8 or not re.search(r'[A-Z]',password) or not re.search(r'[a-z]',password) or not re.search(r'[0-9]',password):
            flash('Password must be min 8 chars with upper, lower, number','danger')
            return redirect(url_for('signup'))
        hashed = generate_password_hash(password)
        try:
            conn = get_db(); cur = conn.cursor()
            cur.execute('INSERT INTO users (username,email,phone,password) VALUES (?,?,?,?)',
                        (username,email,phone,hashed))
            conn.commit(); conn.close()
            flash('Signup successful. Please login.','success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Username or email exists or error','danger')
            return redirect(url_for('signup'))
    return render_template('signup.html')

# Admin credentials
ADMIN_USER = 'admin'
ADMIN_PASSWORD_PLAIN = 'Admin@123'
ADMIN_PASSWORD_HASH = generate_password_hash(ADMIN_PASSWORD_PLAIN)

# -------------------------
# ---------- Admin ----------
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','').strip()
        # check username and password against stored admin constants
        if u == ADMIN_USER and check_password_hash(ADMIN_PASSWORD_HASH, p):
            session['admin'] = ADMIN_USER
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials','danger')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, username, email, phone FROM users')
    users = cur.fetchall()
    conn.close()

    return render_template('admin_users.html', users=users)


@app.route('/admin/delete_user/<int:uid>', methods=['POST'])
def admin_delete_user(uid):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id=?',(uid,))
    conn.commit(); conn.close()
    flash('User deleted','success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin',None)
    return redirect(url_for('login'))

# -------------------------
# OTP Send
# -------------------------
@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip()
    if not email:
        return jsonify({'message': 'Missing email in request'}), 400

    conn = get_db(); cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({'message': 'Email not registered'}), 400
    otp = random.randint(100000, 999999)
    otp_store[email] = str(otp)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(
            EMAIL_ADDRESS,
            email,
            f"Subject: OTP for Password Reset\n\nYour OTP is: {otp}"
        )
        server.quit()
        return jsonify({'message': 'OTP sent to your email'})
    except Exception as e:
        # don't leak inner exception in prod, but okay for dev
        return jsonify({'message': f'Failed to send OTP: {e}'}), 500

# -------------------------
# Forgot Password
# -------------------------
@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        email = request.form.get('email','').strip()
        entered_otp = request.form.get('otp','').strip()
        newpass = request.form.get('new_password','').strip()
        if otp_store.get(email) != entered_otp:
            flash('Invalid OTP','danger')
            return redirect(url_for('forgot'))
        conn = get_db(); cur = conn.cursor()
        cur.execute('SELECT id FROM users WHERE email=?', (email,))
        row = cur.fetchone()
        if row:
            cur.execute('UPDATE users SET password=? WHERE id=?',
                        (generate_password_hash(newpass), row['id']))
            conn.commit()
            conn.close()
            otp_store.pop(email, None)
            flash('Password reset successful. Login with new password.','success')
            return redirect(url_for('login'))
        flash('Email not registered','danger')
        conn.close()
    return render_template('forgot.html')

# -------------------------
# Logout
# -------------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# -------------------------
# Prediction
# -------------------------
@app.route('/predict', methods=['GET','POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))
    fields = [
        'age', 'sex', 'trestbps', 'chol', 'bmi',
        'glucose', 'skin_thickness', 'insulin',
        'cp', 'thalach', 'oldpeak', 'slope',
        'mdvp_fo', 'mdvp_jitter', 'mdvp_shimmer', 'nhr'
    ]
    field_labels = {f:f for f in fields}
    result = {}
    if request.method=='POST':
        vals = []
        for f in fields:
            raw = request.form.get(f, '')
            if raw is None or raw == '':
                # choose default 0 if empty — you may change this behavior
                vals.append(0.0)
                continue
            try:
                vals.append(float(raw))
            except:
                vals.append(0.0)
        X = np.array(vals).reshape(1,-1)
        if unified_scaler:
            try:
                Xs = unified_scaler.transform(X)
            except Exception as e:
                # if scaler fails, fallback to raw X
                print("Scaler transform failed:", e)
                Xs = X
        else:
            Xs = X

        if not unified_models:
            # no models loaded
            result['error'] = {'error': 'No models loaded. Place model .pkl files in the models/ directory.'}
        else:
            for name, model in unified_models.items():
                try:
                    pred = int(model.predict(Xs)[0])
                    proba = None
                    if hasattr(model,'predict_proba'):
                        try:
                            proba = float(model.predict_proba(Xs).max())
                        except:
                            proba = None
                    result[name] = {
                        'prediction': 'Positive' if pred==1 else 'Negative',
                        'confidence': f"{proba*100:.2f}%" if proba is not None else 'N/A'
                    }
                except Exception as e:
                    result[name] = {'error': str(e)}
    # Render the template that you actually provided (predict.html)
    return render_template('predict.html', fields=fields, field_labels=field_labels, result=result, user=session.get('user'))

# -------------------------
if __name__=='__main__':
    app.run(debug=True)
