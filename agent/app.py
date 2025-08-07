from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

import uuid
import os

app = Flask(__name__, template_folder='../webapp')
app.secret_key = 'mehta'

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Temporary in-memory storage for demo
complaints = {}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

users = {
    "krutarthmehta3@gmail.com": generate_password_hash("admin123")
}

@app.route('/manual-complaint')
def manual_complaint():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('chatbot.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_hash = users.get(email)

        if user_hash and check_password_hash(user_hash, password):
            session['user'] = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    category = request.form['category']
    description = request.form['description']
    file = request.files['file']

    complaint_id = str(uuid.uuid4())[:8]  # Shortened UUID

    filename = None
    if file:
        filename = f"{complaint_id}_{file.filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    complaints[complaint_id] = {
        'name': name,
        'email': email,
        'phone': phone,
        'category': category,
        'description': description,
        'file': filename,
        'status': 'Received'
    }

    return render_template('success.html', complaint_id=complaint_id)

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        complaint_id = request.form['complaint_id']
        complaint = complaints.get(complaint_id)
        return render_template('track.html', complaint=complaint, complaint_id=complaint_id)
    return render_template('track.html')


if __name__ == '__main__':
    app.run(debug=True)
