from datetime import datetime, timezone
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
import os
import requests
import boto3
import yaml

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
    email=request.args.get('email')
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('chatbot.html', email=email)

users = {
    "admin@gmail.com": generate_password_hash("admin123"),
    "customer@gmail.com": generate_password_hash("customer123"),
    "tomhyane@gmail.com": generate_password_hash("tom@pass123")
}

support_users={
    "admin@gmail.com": generate_password_hash("admin123"),
    "support@gmail.com": generate_password_hash("support123")
}

chat_history = []

status_counts = {
        'New': 0,
        'In Progress': 0,
        'Completed': 0
    }
trend_data = {}


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
        return "⚠️ Failed to get response from chatbot.<a href='/manual-complaint'>Click here to register a manual complaint.</a>."

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
            return redirect(url_for('dashboard', email=email))
        else:
            return render_template('login.html', error="Invalid email or password.")
    return render_template('login.html')

@app.route('/login-support', methods=['GET', 'POST'])
def loginsupport():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        profile = "support"
        user_hash = support_users.get(email)

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
    
    complaints_list = get_complaints_assigned_to_email(email)
    print("response: "+str(complaints_list))


    # Categorize complaints

    complaints = {
        'new': [],
        'in_progress': [],
        'completed': []
    }

    for complaint in complaints_list:
        status = complaint['status'].lower()
        # check if created_date not in complaint
        
            
        if 'created_date' in complaint:
            trend_data[complaint['created_date']] = trend_data.get(complaint['created_date'], 0) + 1
        if status == 'open':
            complaints['new'].append(complaint)
            status_counts['New'] += 1
        elif status == 'in_progress':
            complaints['in_progress'].append(complaint)
            status_counts['In Progress'] += 1
        elif status == 'completed':
            complaints['completed'].append(complaint)
            status_counts['Completed'] += 1

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
        # complaint = get_complaints.get(complaint_id)
        return render_template('track.html', complaint=complaint, complaint_id=complaint_id)
    return render_template('track.html')

@app.route('/callAgentForAnalysis', methods=['POST'])
def callAgentForAnalysis():
    message= request.get_json().get('message', '')
    try:
        response = requests.post(
            "http://127.0.0.1:8001/analyzeComplaint",
            json={"message": message},
            headers={"Content-Type": "application/json"}
        )
        data = response.json()

        bot_reply = data.get("response", "")
        # print("Bot reply:", bot_reply)
        return jsonify({"message": bot_reply})
    except Exception as e:
        print("Error:", e)
        return jsonify({"message": "⚠️ Failed to get response from chatbot."}), 500

@app.route('/analytics-data')
def analytics_data():
    # status_counts = {
    #     'Pending': 12,
    #     'In Progress': 8,
    #     'Completed': 20
    # }
    # trend_data = {
    #     "2025-08-01": 3,
    #     "2025-08-02": 4,
    #     "2025-08-03": 6,
    #     "2025-08-04": 2,
    #     "2025-08-05": 5
    # }
    return jsonify({"status_counts": status_counts, "trend_data": trend_data})

def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


@app.route('/api/complaint', methods=['POST'])
def create_complaint_api():
    data = request.form
    client_id = data.get('client_id', '1')  # Default client_id if not provided
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    category = data.get('category')
    description = data.get('description')
    print(data)
    file = request.files.get('attachment')
    print("inside complaint api")
    try:
       
        config_path = os.path.join(os.path.dirname(__file__), 'prereqs/prereqs_config.yaml')
        config = read_yaml_file(config_path)
        kb_name = config['knowledge_base_name']

     
        dynamodb = boto3.resource('dynamodb')
        smm_client = boto3.client('ssm')
        table_name = smm_client.get_parameter(Name=f'{kb_name}-table-name', WithDecryption=False)
        table = dynamodb.Table(table_name["Parameter"]["Value"])
        # get today's date
        today = datetime.utcnow().isoformat()
        print(today)
        complaint_id = str(uuid.uuid4())[:8]
        table.put_item(
            Item={
                'client_id': '1',
                'complaint_id': complaint_id,
                'name': name,
                'client_name': name,
                'email': email,
                'phone': phone,
                'category': category,
                'description': description,
                'status': 'open',
                'assignee_email': 'support@gmail.com',
                'created_date': today,
                'priority_level': '2.0'
            }
        )
        print("complaint added")
        return jsonify({"status": "success", "complaint_id": complaint_id}), 200

    except Exception as e:
        print("complaint logging failed")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/complaints_fetch', methods=['GET'])
def get_complaints_by_email():
    email = request.args.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    try:
        config_path = os.path.join(os.path.dirname(__file__), 'prereqs/prereqs_config.yaml')
        config = read_yaml_file(config_path)
        kb_name = config['knowledge_base_name']
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        smm_client = boto3.client('ssm')
        table_name = smm_client.get_parameter(Name=f'{kb_name}-table-name', WithDecryption=False)['Parameter']['Value']
        table = dynamodb.Table(table_name)

        # Query using GSI on 'email'
        response = table.query(
            IndexName='email-index',  # replace with the actual index name
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )

        complaints = response.get('Items', [])
        
        return jsonify({"status": "success", "complaints": complaints}), 200

    except Exception as e:
        print(f"Error fetching complaints: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/user_complaint_tracking")
def user_complaint_tracking():
    email = request.args.get('email')
    print(email)
    complaints_list = get_complaints_raised_by_email(email)
    complaints = {
        'new': [],
        'in_progress': [],
        'completed': []
    }

    for complaint in complaints_list:
        status = complaint['status'].lower()
        # check if created_date not in complaint
        
            
        if 'created_date' in complaint:
            trend_data[complaint['created_date']] = trend_data.get(complaint['created_date'], 0) + 1
        if status == 'open':
            complaints['new'].append(complaint)
            status_counts['New'] += 1
        elif status == 'in_progress':
            complaints['in_progress'].append(complaint)
            status_counts['In Progress'] += 1
        elif status == 'completed':
            complaints['completed'].append(complaint)
            status_counts['Completed'] += 1
    print("response: "+str(complaints_list))
    return render_template("user_complaint_tracking.html", complaints=complaints,email=email)


def get_complaints_assigned_to_email(email):
    # email = request.args.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    try:
        config_path = os.path.join(os.path.dirname(__file__), 'prereqs/prereqs_config.yaml')
        config = read_yaml_file(config_path)
        kb_name = config['knowledge_base_name']
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        smm_client = boto3.client('ssm')
        table_name = smm_client.get_parameter(Name=f'{kb_name}-table-name', WithDecryption=False)['Parameter']['Value']
        table = dynamodb.Table(table_name)

        # Query using GSI on 'email'
        response = table.query(
            IndexName='assignee_email-index',  # replace with the actual index name
            KeyConditionExpression=boto3.dynamodb.conditions.Key('assignee_email').eq(email)
        )

        complaints = response.get('Items', [])
        print(f"Fetched complaints for email {email}: {complaints}")
        return complaints

    except Exception as e:
        print(f"Error fetching complaints: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})


def get_complaints_raised_by_email(email):
    # email = request.args.get('email')
    if not email:
        return jsonify({"status": "error", "message": "Email is required"}), 400

    try:
        config_path = os.path.join(os.path.dirname(__file__), 'prereqs/prereqs_config.yaml')
        config = read_yaml_file(config_path)
        kb_name = config['knowledge_base_name']
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        smm_client = boto3.client('ssm')
        table_name = smm_client.get_parameter(Name=f'{kb_name}-table-name', WithDecryption=False)['Parameter']['Value']
        table = dynamodb.Table(table_name)

        # Query using GSI on 'email'
        response = table.query(
            IndexName='email-index',  # replace with the actual index name
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
        )

        complaints = response.get('Items', [])
        print(f"Fetched complaints for email {email}: {complaints}")
        return complaints

    except Exception as e:
        print(f"Error fetching complaints: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
