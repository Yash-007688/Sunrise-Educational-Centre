from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash, jsonify
import os
import secrets
from werkzeug.utils import secure_filename
from auth_handler import (
    init_db, register_user, authenticate_user, save_resource, get_all_resources,
    delete_resource, get_all_users, delete_user, search_users, get_user_by_id,
    update_user, add_notification, get_unread_notifications_for_user, get_all_notifications,
    create_live_class, get_live_class, get_active_classes, deactivate_class,
    get_class_details_by_id, get_all_classes, get_resources_for_class_id,
    mark_notification_as_seen, delete_notification,
    save_forum_message, get_forum_messages, vote_on_message, delete_forum_message
)

app = Flask(__name__, static_folder='.', template_folder='.')
app.secret_key = 'your_secret_key_here'  # Change this to a secure random value in production

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'png', 'jpg', 'jpeg'}
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_global_variables():
    user_id = session.get('user_id')
    username = session.get('username')
    role = session.get('role')
    notifications = []
    if user_id:
        notifications = get_unread_notifications_for_user(user_id)
            
    all_classes = get_all_classes()
    return dict(user_notifications=notifications, all_classes=all_classes, username=username, role=role)

# Route for the main page
@app.route('/')
def home():
    return render_template('index.html')

# Route for study resources
@app.route('/study-resources')
def study_resources():
    role = session.get('role')

    # Redirect if not logged in
    if not role:
        flash('You must be logged in to view resources.', 'error')
        return redirect(url_for('auth'))
    
    # Redirect admin/teacher to their own panel, as this page is for students
    if role in ['admin', 'teacher']:
        flash('Please use the admin panel to manage all resources.', 'info')
        return redirect(url_for('admin_panel'))

    # Get class_id from the role name stored in the session
    all_classes_dict_rev = {c[1]: c[0] for c in get_all_classes()}
    class_id = all_classes_dict_rev.get(role)
    
    # Fetch resources only for the user's class
    resources = []
    if class_id:
        resources = get_resources_for_class_id(class_id)

    user_id = session.get('user_id')
    paid_status = None
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            paid_status = user[3]  # Assuming user[3] is the paid status

    return render_template('study-resources.html', resources=resources, class_name=role, paid_status=paid_status)

# Route for forum
@app.route('/forum')
def forum():
    username = session.get('username')
    if not username:
        flash('You must be logged in to view the forum.', 'error')
        return redirect(url_for('auth'))
    return render_template('forum.html', username=username)

@app.route('/api/forum/messages', methods=['GET'])
def api_get_forum_messages():
    messages = get_forum_messages()
    return jsonify([
        {
            'id': m[0], 'user_id': m[1], 'username': m[2], 'message': m[3],
            'parent_id': m[4], 'upvotes': m[5], 'downvotes': m[6], 'timestamp': m[7]
        } for m in messages
    ])

@app.route('/api/forum/messages', methods=['POST'])
def api_post_forum_message():
    user_id = session.get('user_id')
    username = session.get('username')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    message = data.get('message')
    parent_id = data.get('parent_id')
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    save_forum_message(user_id, username, message, parent_id)
    return jsonify({'success': True}), 201

@app.route('/api/forum/messages/<int:message_id>/replies', methods=['GET'])
def api_get_message_replies(message_id):
    replies = get_forum_messages(parent_id=message_id)
    return jsonify([
        {
            'id': r[0], 'user_id': r[1], 'username': r[2], 'message': r[3],
            'parent_id': r[4], 'upvotes': r[5], 'downvotes': r[6], 'timestamp': r[7]
        } for r in replies
    ])

@app.route('/api/forum/messages/<int:message_id>/vote', methods=['POST'])
def api_vote_on_message(message_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    vote_type = data.get('vote_type')
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({'error': 'Invalid vote type'}), 400
    vote_on_message(message_id, vote_type)
    return jsonify({'success': True})

@app.route('/api/forum/messages/<int:message_id>', methods=['DELETE'])
def api_delete_forum_message(message_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    delete_forum_message(message_id)
    return jsonify({'success': True})

# Route for online class
@app.route('/online-class', methods=['GET', 'POST'])
def online_class():
    if request.method == 'POST':
        code = request.form.get('class_code')
        pin = request.form.get('pin')
        meeting_url = get_live_class(code, pin)
        if meeting_url:
            return render_template('online-class.html', meeting_url=meeting_url)
        else:
            flash('Invalid class code or PIN. Please try again.', 'error')
    return render_template('online-class.html', meeting_url=None)

# Route for authentication (login)
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    error = None
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        all_classes_dict = {str(c[0]): c[1] for c in get_all_classes()}
        selected_role = all_classes_dict.get(class_id)
        username = request.form.get('username')
        password = request.form.get('password')
        admin_code = request.form.get('admin_code')
        if selected_role == 'admin':
            if admin_code != 'sec@011':
                error = 'Invalid admin code. Login denied.'
                return render_template('auth.html', error=error)
        user_data = authenticate_user(username, password)
        if user_data:
            user_id, user_role = user_data
            if user_role == selected_role:
                session['user_id'] = user_id
                session['username'] = username
                session['role'] = user_role
                if user_role in ['admin', 'teacher']:
                    return redirect(url_for('admin_panel'))
                else:
                    return redirect(url_for('home'))
        error = 'Invalid username, password, or role.'
    return render_template('auth.html', error=error)

# Route for registration
@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    class_id = request.form.get('class_id')
    
    all_classes_dict = {str(c[0]): c[1] for c in get_all_classes()}
    role = all_classes_dict.get(class_id)
    
    admin_code = request.form.get('admin_code')
    if role == 'admin':
        if admin_code != 'sec@011':
            return render_template('auth.html', error='Invalid admin code. Registration denied.')
            
    if register_user(username, password, class_id):
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth'))
    else:
        return render_template('auth.html', error='Username already exists. Please choose another.')

# Admin panel route
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    if session.get('role') in ['admin', 'teacher']:
        resources = get_all_resources()
        q = request.args.get('q', '').strip()
        users = search_users(q) if q else get_all_users()
        all_notifications = get_all_notifications()
        active_classes = get_active_classes()
        return render_template('admin.html', resources=resources, users=users, search_query=q, all_notifications=all_notifications, active_classes=active_classes)
    else:
        return redirect(url_for('auth'))

@app.route('/create-live-class', methods=['GET', 'POST'])
def create_live_class_page():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    
    if request.method == 'POST':
        topic = request.form.get('topic')
        description = request.form.get('description')
        room_name = f"SunriseEducation-{secrets.token_hex(8)}"
        meeting_url = f"https://meet.jit.si/{room_name}"
        class_code = ''.join(secrets.choice('0123456789') for i in range(6))
        pin = ''.join(secrets.choice('0123456789') for i in range(4))
        new_class_id = create_live_class(class_code, pin, meeting_url, topic, description)
        details = get_class_details_by_id(new_class_id)
        class_details = {
            'topic': details[3], 'description': details[4],
            'code': details[0], 'pin': details[1], 'url': details[2]
        }
        return render_template('create_class.html', class_details=class_details)
        
    return render_template('create_class.html', class_details=None)

@app.route('/end-live-class/<int:class_id>', methods=['POST'])
def end_live_class(class_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    deactivate_class(class_id)
    flash("Live class has been ended.", 'info')
    return redirect(url_for('admin_panel'))

# Upload resource route
@app.route('/upload-resource', methods=['GET', 'POST'])
def upload_resource():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        file = request.files.get('file')
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        if not file or file.filename == '' or not class_id or not category:
            flash('File, class, and category selection are required.', 'error')
        elif not allowed_file(file.filename):
            flash('File type not allowed.', 'error')
        else:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            save_resource(filename, class_id, filepath, title, description, category)
            flash('Resource uploaded successfully!', 'success')
            return redirect(url_for('admin_panel'))
    return render_template('upload_resource.html')

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Serve static files (CSS, JS, images, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    # Serve any file in the root or subfolders
    return send_from_directory('.', filename)

# Delete resource route
@app.route('/delete-resource/<filename>', methods=['POST'])
def delete_resource_route(filename):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    # Remove file from uploads folder
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    # Remove from database
    delete_resource(filename)
    return redirect(url_for('admin_panel'))

# Delete user route
@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user_route(user_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    delete_user(user_id)
    return redirect(url_for('admin_panel'))

# User info route
@app.route('/user-info/<int:user_id>', methods=['GET', 'POST'])
def user_info(user_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    user = get_user_by_id(user_id)
    if not user:
        return redirect(url_for('admin_panel'))
    error = None
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_class_id = request.form.get('class_id')
        new_paid = request.form.get('paid')
        if not all([new_username, new_class_id, new_paid]):
            error = 'Username, role, and paid status are required.'
        else:
            update_user(user_id, new_username, new_class_id, new_paid)
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin_panel'))
    return render_template('user_info.html', user=user, error=error)

@app.route('/add-notification', methods=['POST'])
def add_notification_route():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    message = request.form.get('message')
    class_id = request.form.get('class_id')
    if message and class_id:
        add_notification(message, class_id)
        flash('Notification sent!', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth'))

@app.route('/mark-notification-seen', methods=['POST'])
def mark_notification_seen_route():
    user_id = session.get('user_id')
    if not user_id:
        return {'status': 'error', 'message': 'User not logged in'}, 401
    
    data = request.json
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return {'status': 'error', 'message': 'Notification ID is required'}, 400
        
    mark_notification_as_seen(user_id, notification_id)
    return {'status': 'success'}

@app.route('/delete-notification/<int:notification_id>', methods=['POST'])
def delete_notification_route(notification_id):
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
    delete_notification(notification_id)
    flash('Notification deleted!', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port) 