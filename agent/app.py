<<<<<<< Updated upstream
from flask import Flask, render_template, request, redirect, url_for, session
=======
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
>>>>>>> Stashed changes
from werkzeug.security import check_password_hash, generate_password_hash
import boto3
import yaml  



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

<<<<<<< Updated upstream

=======
@app.route('/complaints')
def get_complaints():
    return jsonify([
        {"id": 1, "title": "Network issue", "status": "New", "description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 2, "title": "Login problem", "status": "InProgress","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 3, "title": "Payment failure", "status": "completed","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 4, "title": "Billing", "status": "New","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 5, "title": "Order placement", "status": "InProgress","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 6, "title": "Payment stuck", "status": "completed","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"}
    ])
def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

@app.route('/api/complaint', methods=['POST'])
def create_complaint_api():
    data = request.form
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    category = data.get('category')
    description = data.get('description')

    file = request.files.get('attachment')

    try:
       
        config_path = os.path.join(os.path.dirname(__file__), 'prereqs/prereqs_config.yaml')
        config = read_yaml_file(config_path)
        kb_name = config['knowledge_base_name']

     
        dynamodb = boto3.resource('dynamodb')
        smm_client = boto3.client('ssm')
        table_name = smm_client.get_parameter(Name=f'{kb_name}-table-name', WithDecryption=False)
        table = dynamodb.Table(table_name["Parameter"]["Value"])

        complaint_id = str(uuid.uuid4())[:8]
        table.put_item(
            Item={
                'complaint_id': complaint_id,
                'name': name,
                'email': email,
                'phone': phone,
                'category': category,
                'description': description,
                'status': 'open'
            }
        )

        return jsonify({"status": "success", "complaint_id": complaint_id}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
    
>>>>>>> Stashed changes
if __name__ == '__main__':
    app.run(debug=True)
