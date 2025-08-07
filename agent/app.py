import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import uuid
import os

app = Flask(__name__, template_folder='../webapp', static_folder='../static')

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
    return render_template('chatbot.html')

users = {
    "admin@gmail.com": generate_password_hash("admin123")
}

chat_history = []

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message')
    if not user_message:

        return jsonify({'reply': 'No message received'}), 400

    # TODO: Call your AI model or LLM backend here
    ai_reply = generate_ai_response(user_message)

    # Log message + response
    chat_history.append({
        'timestamp': datetime.utcnow().isoformat(),
        'user': user_message,
        'bot': ai_reply
    })

    return jsonify({'reply': ai_reply})

# Dummy AI responder function (replace with actual logic)
def generate_ai_response(message):
    # Here, you can call AWS Bedrock, OpenAI API, or your own model
    try:
        response = requests.post(
            "http://127.0.0.1:8000/endUserChat",
            json={"message": message},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()
        bot_reply = data.get("response", "")
        return bot_reply
    except Exception as e:
        print("Error:", e)
        return "⚠️ Failed to get response from chatbot."

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

@app.route('/login-support', methods=['GET', 'POST'])
def loginsupport():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        profile = "support"
        user_hash = users.get(email)

        if user_hash and check_password_hash(user_hash, password):
            session['user'] = email                
            return redirect(url_for('kanban_board',email=email))
        else:
            return render_template('login-support.html', error="Invalid email or password.")
    return render_template('login-support.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/logout-support',methods=['GET','POST'])
def logoutsupport():
    session.pop('user', None)
    return redirect(url_for('loginsupport'))

@app.route('/kanban')
def kanban_board():
    email = request.args.get('email')
    complaints_list = [
        {"id": 1, "title": "Network issue", "status": "New", "description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 2, "title": "Login problem", "status": "InProgress","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 3, "title": "Payment failure", "status": "completed","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 4, "title": "Billing", "status": "New","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 5, "title": "Order placement", "status": "InProgress","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"},
        {"id": 6, "title": "Payment stuck", "status": "completed","description": "Unable to connect to the internet.", "created_at": "2023-10-01","raised_by": "John Doe", "assigned_to_group": "Support Team"}
    ]


    # Categorize complaints
    complaints = {
        'new': [],
        'in_progress': [],
        'completed': []
    }

    for complaint in complaints_list:
        status = complaint['status'].lower()
        if status == 'new':
            complaints['new'].append(complaint)
        elif status == 'inprogress':
            complaints['in_progress'].append(complaint)
        elif status == 'completed':
            complaints['completed'].append(complaint)

    return render_template('kanbansupport.html', complaints=complaints,email=email)

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
        complaint = get_complaints.get(complaint_id)
        return render_template('track.html', complaint=complaint, complaint_id=complaint_id)
    return render_template('track.html')

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

if __name__ == '__main__':
    app.run(debug=True)
