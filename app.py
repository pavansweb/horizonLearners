from flask import Flask, request, render_template, jsonify, redirect, url_for, session, flash, send_from_directory, abort
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from enum import Enum
from functools import wraps
import os
import requests

# Configuration
class Role(Enum):
    USER = 'user'
    ADMIN = 'admin'

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads/profile_pics'  # Directory for uploaded files
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'accountdatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
CORS(app)  # Enable CORS for cross-origin requests

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
RESTRICTED_IMAGES_FOLDER = 'restricted_images'
os.makedirs(RESTRICTED_IMAGES_FOLDER, exist_ok=True)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(120), default='/static/icons/user-profile.png')
    role = db.Column(db.Enum(Role), default=Role.USER)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Role-based access control decorator
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                abort(401)  # Raise 401 Unauthorized error if user is not logged in
            user = db.session.get(User, session['user_id'])
            if user.role != required_role:
                abort(403)  # Raise 403 Forbidden error if user does not have the required role
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Routes

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('401.html'), 401


@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



@app.route('/')
def index():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        profile_picture = user.profile_picture if user else '/static/icons/user-profile.png'
        print(f"User found: {user.email}, Profile picture: {profile_picture}")
        return render_template('index.html', logged_in=True, profile_picture=profile_picture)
    print("User not logged in")
    return render_template('index.html', logged_in=False)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_body = request.form.get('message')

        if not all([name, email, subject, message_body]):
            flash('All fields are required!', 'error')
            return redirect(url_for('contact'))

        msg = Message(
            subject=subject,
            sender=os.getenv('MAIL_USERNAME'),
            recipients=['pavansh555@gmail.com', 'elitex989@gmail.com'],
            body=f"Sender Name: {name}\nUsers Email: {email}\n\nSubject: {subject}\n\nMessage: \n{message_body}"
        )

        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")
    if request.method == 'GET':
        try:
            print("Rendering login.html")
            return render_template('login.html')
        except Exception as e:
            print(f"Error rendering login.html: {e}")
    else:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        print(f"Login attempt - Email: {email}")

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            print(f"Login successful for user: {user.email}")
            return jsonify({'message': 'Login successful'})

        print("Invalid credentials")
        return jsonify({'message': 'Invalid credentials'}), 401



@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', Role.USER.value)  # Default role is USER

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password, role=Role(role))
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})

@app.route('/user', methods=['GET'])
def user_info():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        if user:
            return jsonify({
                'email': user.email,
                'joined': user.created_at.strftime('%Y-%m-%d'),
                'profile_picture': user.profile_picture
            })
    return jsonify({'message': 'User not found or not logged in'}), 404

@app.route('/view-users', methods=['GET'])
@role_required(Role.ADMIN)
def view_users():
    user = db.session.get(User, session['user_id'])
    if user and user.role == Role.ADMIN:
        users = User.query.all()
        users_data = [{
            'email': user.email,
            'role': user.role.value,
            'joined': user.created_at.strftime('%Y-%m-%d'),
            'password_hash': user.password_hash  # Include hashed password
        } for user in users]
        return jsonify(users_data)
    return jsonify({'message': 'Unauthorized'}), 403



@app.route('/manage-users', methods=['GET'])
@role_required(Role.ADMIN)
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)


@app.route('/assign-role/<int:user_id>', methods=['POST'])
@role_required(Role.ADMIN)
def assign_role(user_id):
    new_role = request.form.get('role')

    if new_role not in [role.value for role in Role]:
        flash('Invalid role', 'error')
        return redirect(url_for('manage_users'))

    user = User.query.get(user_id)
    if user:
        user.role = Role(new_role)
        db.session.commit()
        flash(f'Role updated to {new_role} successfully', 'success')
    else:
        flash('User not found', 'error')

    return redirect(url_for('manage_users'))

@app.route('/userinfo/<int:user_id>', methods=['GET'])
@role_required(Role.ADMIN)
def userinfo(user_id):
    user = User.query.get(user_id)
    if user:
        return render_template('userinfo.html', 
                               user={
                                   'email': user.email,
                                   'joined': user.created_at.strftime('%Y-%m-%d'),
                                   'profile_picture': user.profile_picture
                               })
    return jsonify({'message': 'User not found'}), 404

@app.route('/upload-profile-picture', methods=['POST'])
def upload_profile_picture():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        if 'user_id' not in session:
            return jsonify({'message': 'User not logged in'}), 401

        user = db.session.get(User, session['user_id'])
        if not user:
            return jsonify({'message': 'User not found'}), 404

        if user.profile_picture and user.profile_picture != '/static/icons/user-profile.png':
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(user.profile_picture))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        email = user.email
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{email}.{ext}"

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        user.profile_picture = url_for('get_profile_picture', filename=filename)
        db.session.commit()

        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'profile_picture_url': user.profile_picture
        })

    return jsonify({'message': 'File type not allowed'}), 400

@app.route('/profile-pic/<filename>')
def get_profile_picture(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Helper functions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def github_upload_file(filename, file_content):
    url = f'https://api.github.com/repos/{os.getenv("GITHUB_REPO")}/contents/{os.getenv("GITHUB_PATH")}/{filename}'
    headers = {
        'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
        'Content-Type': 'application/json'
    }
    data = {
        'message': f'Upload {filename}',
        'content': file_content,
        'branch': 'main'
    }
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def github_delete_file(filename):
    url = f'https://api.github.com/repos/{os.getenv("GITHUB_REPO")}/contents/{os.getenv("GITHUB_PATH")}/{filename}'
    headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    sha = response.json()['sha']
    delete_url = url
    data = {
        'message': f'Delete {filename}',
        'sha': sha,
        'branch': 'main'
    }
    response = requests.delete(delete_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

# Run the application
if __name__ == '__main__':
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        db.create_all()  # Ensure the database is created

    app.run(host='0.0.0.0', port=3000, debug=True)
