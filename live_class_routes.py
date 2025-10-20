from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
from .daily_handler import daily_handler

# Separate blueprint for live class routes
live_classes_bp = Blueprint('live_classes', __name__)

DATABASE = 'users.db'

@live_classes_bp.route('/online-class', methods=['GET'])
def online_class():
	user_id = session.get('user_id')
	role = session.get('role')
	username = session.get('username')
	if not user_id or not role:
		flash('You must be logged in to access the online class.', 'error')
		return redirect(url_for('auth'))

	from auth_handler import get_upcoming_live_classes, get_active_live_classes, get_completed_live_classes
	upcoming_classes = get_upcoming_live_classes()
	active_classes = get_active_live_classes()
	completed_classes = get_completed_live_classes()
	
	return render_template('online-class.html', role=role, username=username,
							upcoming_classes=upcoming_classes,
							active_classes=active_classes,
							completed_classes=completed_classes)

@live_classes_bp.route('/join-class/<int:class_id>')
def join_class(class_id):
    if not session.get('user_id'):
        flash('You must be logged in to join a class.', 'error')
        return redirect(url_for('auth'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT topic, description, target_class, class_stream, subject, teacher_name, status FROM live_classes WHERE id=?', (class_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        flash('Class not found.', 'error')
        return redirect(url_for('live_classes.online_class'))
        
    topic, description, target_class, class_stream, subject, teacher_name, status = row
    
    if status != 'active':
        flash('This class is not currently active.', 'error')
        return redirect(url_for('live_classes.online_class'))
        
    # Get Daily.co room URL
    daily_response = daily_handler.get_room(class_id)
    if not daily_response.json.get('success'):
        flash('Failed to get class room. Please try again.', 'error')
        return redirect(url_for('live_classes.online_class'))
        
    meeting_url = daily_response.json['room_url']
    
    # Log attendance
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO class_attendance
            (class_id, student_id, join_time)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (class_id, session['user_id']))
        conn.commit()
    except Exception as e:
        print(f"Error logging attendance: {e}")
    finally:
        conn.close()

    return render_template('join_class.html', 
                         class_id=class_id, 
                         meeting_url=meeting_url,
                         topic=topic, 
                         description=description,
                         target_class=target_class,
                         class_stream=class_stream,
                         subject=subject,
                         teacher_name=teacher_name)

@live_classes_bp.route('/join-class-host/<int:class_id>')
def join_class_host(class_id):
    if session.get('role') not in ['admin', 'teacher']:
        flash('Access denied. Only hosts can access this page.', 'error')
        return redirect(url_for('admin_panel'))
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT topic, description, target_class, class_stream, subject, teacher_name, status FROM live_classes WHERE id=?', (class_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        flash('Class not found.', 'error')
        return redirect(url_for('admin_panel'))
        
    topic, description, target_class, class_stream, subject, teacher_name, status = row
    
    if status != 'active':
        flash('This class is not currently active.', 'error')
        return redirect(url_for('admin_panel'))
        
    # Get Daily.co room URL
    daily_response = daily_handler.get_room(class_id)
    if not daily_response.json.get('success'):
        # Try creating new room if it doesn't exist
        daily_response = daily_handler.create_room(class_id)
        if not daily_response.json.get('success'):
            flash('Failed to create class room. Please try again.', 'error')
            return redirect(url_for('admin_panel'))
            
    meeting_url = daily_response.json['room_url']
    
    return render_template('join_class_host.html',
                         class_id=class_id,
                         meeting_url=meeting_url,
                         topic=topic,
                         description=description,
                         target_class=target_class,
                         class_stream=class_stream,
                         subject=subject,
                         teacher_name=teacher_name)

@live_classes_bp.route('/start-live-class', methods=['POST'])
def start_live_class_route():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
        
    class_id = request.form.get('class_id')
    if class_id is not None:
        class_id = int(class_id)
    
    from auth_handler import can_start_class, start_live_class, add_notification
    if not can_start_class(class_id):
        flash('This class cannot be started yet. Check the scheduled time.', 'error')
        return redirect(url_for('live_classes.online_class'))
    
    # Create Daily.co room
    daily_response = daily_handler.create_room(class_id)
    if not daily_response.json.get('success'):
        flash('Failed to create class room. Please try again.', 'error')
        return redirect(url_for('live_classes.online_class'))
        
    # Start the class
    start_live_class(class_id)
    
    # Store Daily.co room URL
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('UPDATE live_classes SET room_url = ? WHERE id = ?', 
                 (daily_response.json['room_url'], class_id))
        conn.commit()
    finally:
        conn.close()
    
    # Notify users
    add_notification('A live class has started! Join now.', class_id, 'all', 'active', 
                    notification_type='live_class')
    flash('Live class started!', 'success')
    return redirect(url_for('live_classes.join_class_host', class_id=class_id))

@live_classes_bp.route('/end-live-class', methods=['POST'])
def end_live_class_route():
    if session.get('role') not in ['admin', 'teacher']:
        return redirect(url_for('auth'))
        
    class_id = request.form.get('class_id')
    if class_id is not None:
        class_id = int(class_id)
    
    from auth_handler import can_end_class, end_live_class
    if not can_end_class(class_id):
        flash('This class cannot be ended. It may not be active.', 'error')
        return redirect(url_for('live_classes.online_class'))
    
    # Delete Daily.co room
    daily_handler.delete_room(class_id)
    
    # End the class
    end_live_class(class_id)
    
    flash('Live class ended and moved to completed section.', 'info')
    return redirect(url_for('live_classes.online_class'))

@live_classes_bp.route('/api/live-class/<int:class_id>/recording', methods=['POST'])
def control_recording(class_id):
    """Control recording for a live class"""
    if session.get('role') not in ['admin', 'teacher']:
        return jsonify({
            'success': False,
            'error': 'Unauthorized'
        }), 403

    try:
        action = request.json.get('action')
        if action not in ['start', 'stop']:
            return jsonify({
                'success': False,
                'error': 'Invalid action'
            }), 400

        # Check if class exists and is active
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('SELECT status FROM live_classes WHERE id = ?', (class_id,))
        row = c.fetchone()
        if not row or row[0] != 'active':
            return jsonify({
                'success': False,
                'error': 'Class not found or not active'
            }), 404

        # Control recording
        if action == 'start':
            return daily_handler.start_recording(class_id)
        else:
            return daily_handler.stop_recording(class_id)

    except Exception as e:
        print(f'Error controlling recording: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to control recording',
            'message': str(e)
        }), 500

@live_classes_bp.route('/host-stream/<class_id>')
def host_stream_page(class_id):
	"""Page that displays the host's camera stream"""
	try:
		conn = sqlite3.connect(DATABASE)
		c = conn.cursor()
		c.execute('SELECT topic, description FROM live_classes WHERE id = ?', (class_id,))
		class_data = c.fetchone()
		conn.close()
		if not class_data:
			return "Class not found", 404
		topic, description = class_data
		return render_template('host_stream.html', 
							 class_id=class_id, 
							 topic=topic or 'Live Class',
							 description=description or '')
	except Exception as e:
		print(f"Error loading host stream page: {e}")
		return "Error loading stream", 500