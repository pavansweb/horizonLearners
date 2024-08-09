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
from itsdangerous import URLSafeTimedSerializer as Serializer
import logging

# Configuration
class Role(Enum):
    USER = 'user'
    ADMIN0 = 'admin0'  # Full access
    ADMIN1 = 'admin1'  # Limited admin
    ADMIN2 = 'admin2'  # More limited admin

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management
app.config['UPLOAD_FOLDER'] = 'uploads/profile_pics'  # Directory for uploaded files
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'horizonmailer555@gmail.com'
app.config['MAIL_PASSWORD'] = 'sutd tgxd pgmk lice'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'accountdatabase.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # For creating secure tokens

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
CORS(app)  # Enable CORS for cross-origin requests

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up a custom logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('horizon')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(120), default='/static/icons/user-profile.png')
    role = db.Column(db.Enum(Role), default=Role.USER)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(120), unique=True, nullable=True)
    name = db.Column(db.String(100), default='user')  # Updated name field

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Role-based access control decorator
def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                abort(401)
            user = db.session.get(User, session['user_id'])
            if not user or user.role.value not in [role.value for role in required_roles]:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Routes deleted already

@app.errorhandler(401)
def unauthorized_error(error):
    logger.warning(f"Unauthorized access attempt")
    return render_template('401.html'), 401

@app.errorhandler(403)
def forbidden_error(error):
    logger.warning(f"Forbidden access attempt")
    return render_template('403.html'), 403

@app.errorhandler(404)
def page_not_found(error):
    logger.warning(f"Page not found: {request.url}")
    return render_template('404.html'), 404

@app.route('/')
def index():
    if 'user_id' in session:
        user = db.session.get(User, session['user_id'])
        profile_picture = user.profile_picture if user else '/static/icons/user-profile.png'
        user_name = user.name if user else 'user'
        logger.info(f"{user_name} just accessed the homepage")
        return render_template('index.html', logged_in=True, profile_picture=profile_picture, user_name=user_name)
    logger.info("A non-logged in user accessed the homepage")
    return render_template('index.html', logged_in=False)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message_body = request.form.get('message')

        # Check if all fields are provided
        if not all([name, email, subject, message_body]):
            flash('All fields are required!', 'error')
            return redirect(url_for('contact'))

        # Create the email message
        msg = Message(
            subject=subject,
            sender='horizonmailer555@gmail.com',
            recipients=['pavansh555@gmail.com', 'elitex989@gmail.com'],
            body=f"Sender Name: {name}\nUser's Email: {email}\n\nSubject: {subject}\n\nMessage: \n{message_body}"
        )

        try:
            # Send the email
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
            logger.info(f"Contact form submitted by {name}")
            return redirect(url_for('thank_you_for_contacting'))
        except Exception as e:
            # Handle exceptions
            flash(f'An error occurred: {str(e)}', 'error')
            logger.error(f"Error sending contact form: {str(e)}")
            return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/thank-you-for-contacting')
def thank_you_for_contacting():
    return render_template('thank_you_for_contacting.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Render the login page
        logger.info("Login page accessed")
        return render_template('login.html')

    if request.method == 'POST':
        # Handle the login form submission
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            if user.is_verified:
                session['user_id'] = user.id
                logger.info(f"{user.name} just logged in")
                return jsonify({'message': 'Login successful'})
            else:
                logger.info(f"Unverified account login attempt: {email}")
                return jsonify({'message': 'Account not verified. Please check your email to verify your account.'}), 403

        logger.warning(f"Invalid login attempt: {email}")
        return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', Role.USER.value)
    name = data.get('name', 'user')  # Get name from request, default to 'user'

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    if User.query.filter_by(email=email).first():
        logger.warning(f"Attempted registration with existing email: {email}")
        return jsonify({'message': 'Email already registered'}), 400

    hashed_password = generate_password_hash(password)
    verification_token = generate_confirmation_token(email)
    new_user = User(email=email, password_hash=hashed_password, role=Role(role), verification_token=verification_token, name=name)
    db.session.add(new_user)
    db.session.commit()

    # Send verification email
    verification_url = url_for('verify_email', token=verification_token, _external=True)
    msg = Message('Confirm Your Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Please click the link to verify your email: {verification_url}'
    try:
        mail.send(msg)
        logger.info(f"New user registered: {email}")
    except Exception as e:
        logger.error(f"Error sending verification email to {email}: {e}")
        return jsonify({'message': 'Registration successful, but email could not be sent.'}), 500

    return jsonify({'message': 'Registration successful. Please check your email to verify your account.'}), 200

def generate_confirmation_token(email):
    s = Serializer(app.config['SECRET_KEY'], salt='email-confirm')
    return s.dumps({'email': email})

def confirm_token(token, expiration=3600):
    s = Serializer(app.config['SECRET_KEY'], salt='email-confirm')
    try:
        data = s.loads(token, max_age=expiration)
    except Exception as e:
        logger.error(f"Error confirming token: {str(e)}")
        return False
    return data

@app.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    print(f"Received token: {token}")
    data = confirm_token(token)
    if data is None:
        flash('The verification link is invalid or has expired.', 'error')
        return redirect(url_for('index'))

    user = User.query.filter_by(email=data['email']).first_or_404()
    if user.is_verified:
        flash('Account already verified. You are now logged in.', 'info')
        session['user_id'] = user.id  # Automatically log the user in
    else:
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        session['user_id'] = user.id  # Automatically log the user in
        flash('Your account has been verified. You are now logged in.', 'success')

    return redirect(url_for('index'))


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if request.method == 'POST':
        data = request.form
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required!', 'error')
            return redirect(url_for('change_password'))

        if not check_password_hash(user.password_hash, current_password):
            flash('Current password is incorrect!', 'error')
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash('New passwords do not match!', 'error')
            return redirect(url_for('change_password'))

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('change_password.html')


@app.route('/registration-confirmation/<email>', methods=['GET'])
def registration_confirmation(email):
    return render_template('registration_confirmation.html', email=email)

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
                'profile_picture': user.profile_picture,
                'name': user.name  # Include the name field
            })
    # Return a response for non-logged-in users
    return jsonify({
        'email': None,
        'joined': None,
        'profile_picture': '/static/icons/user-profile.png',
        'name': None
    })




@app.route('/admin', methods=['GET'])
@role_required([Role.ADMIN0, Role.ADMIN1, Role.ADMIN2])
def admin():
    # Print a message to the console when an admin accesses the admin page
    user = db.session.get(User, session['user_id'])
    print(f"Admin user {user.email} accessed the admin page.")

    user_count = User.query.count()
    message_count = ContactMessage.query.count()


    return render_template('admin.html', user_count=user_count, message_count=message_count)


@app.route('/view-users', methods=['GET'])
@role_required([Role.ADMIN0, Role.ADMIN1])
def view_users():
    user = db.session.get(User, session['user_id'])

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
@role_required([Role.ADMIN0, Role.ADMIN1, Role.ADMIN2])
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/delete-user/<int:user_id>', methods=['POST'])
@role_required([Role.ADMIN0])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        # Delete the user's profile picture if it exists
        if user.profile_picture and user.profile_picture != '/static/icons/user-profile.png':
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(user.profile_picture))
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    else:
        flash('User not found', 'error')

    return redirect(url_for('manage_users'))



@app.route('/assign-role/<int:user_id>', methods=['POST'])
@role_required([Role.ADMIN0, Role.ADMIN1, Role.ADMIN2])
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
@role_required([Role.ADMIN0, Role.ADMIN1, Role.ADMIN2])
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

@app.route('/update-name', methods=['POST'])
def update_name():
    if 'user_id' not in session:
        return jsonify({'message': 'User not logged in'}), 401

    user = db.session.get(User, session['user_id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.json
    new_name = data.get('name')

    if not new_name:
        return jsonify({'message': 'Name is required'}), 400

    user.name = new_name

    db.session.commit()

    return jsonify({'success': True, 'message': 'Name updated successfully'})



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





# Run the application
if __name__ == '__main__':
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        db.create_all()  # Ensure the database is created

    app.run(host='0.0.0.0', port=3000, debug=True)

