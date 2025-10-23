#!/usr/bin/env python3
"""
Script to create a test live class for demonstration purposes
"""

import sqlite3
import secrets
from datetime import datetime, timedelta
from auth_handler import create_live_class, add_notification

# Database configuration
DATABASE = 'users.db'

def create_demo_live_class():
    """Create a demonstration live class"""
    
    # Generate unique class code and PIN
    class_code = ''.join(secrets.choice('0123456789') for i in range(6))
    pin = ''.join(secrets.choice('0123456789') for i in range(4))
    
    # Set the class to start in 5 minutes (for testing)
    scheduled_time = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
    
    # Class details
    topic = "Mathematics - Quadratic Equations and Functions"
    description = "Live interactive session covering quadratic equations, graphing parabolas, and real-world applications. Students can ask questions in real-time through chat and polls!"
    meeting_url = f"/join-class/{class_code}"
    
    # Additional parameters
    target_class = "Class 11"  # or "all" for all classes
    class_stream = "Science"  # Science/Commerce/Arts or None
    class_type = "lecture"  # lecture/doubt-session/revision
    paid_status = "unpaid"  # unpaid/paid (determines who can access)
    subject = "Maths"
    teacher_name = "Mohit sir"
    status = "active"  # active = live now, scheduled = for future
    
    # Create the live class
    print("Creating Live Class...")
    print("=" * 60)
    
    try:
        new_class_id = create_live_class(
            class_code=class_code,
            pin=pin,
            meeting_url=meeting_url,
            topic=topic,
            description=description,
            status=status,
            scheduled_time=scheduled_time,
            target_class=target_class,
            class_stream=class_stream,
            class_type=class_type,
            paid_status=paid_status,
            subject=subject,
            teacher_name=teacher_name
        )
        
        print(f"Live Class Created Successfully!")
        print("=" * 60)
        print(f"\nCLASS DETAILS:")
        print(f"   Class ID: {new_class_id}")
        print(f"   Topic: {topic}")
        print(f"   Teacher: {teacher_name}")
        print(f"   Subject: {subject}")
        print(f"   Target: {target_class} ({class_stream})")
        print(f"   Type: {class_type}")
        print(f"   Access: {paid_status.upper()}")
        print(f"   Status: {status.upper()}")
        print(f"   Scheduled: {scheduled_time}")
        print(f"\nACCESS CREDENTIALS:")
        print(f"   Class Code: {class_code}")
        print(f"   PIN: {pin}")
        print(f"\nLINKS:")
        print(f"   Host Page: http://localhost:10000/join-class-host/{new_class_id}")
        print(f"   Student Page: http://localhost:10000{meeting_url}")
        print(f"\nFEATURES ENABLED:")
        print(f"   * Live Video Streaming (WebRTC)")
        print(f"   * Real-time Chat")
        print(f"   * Interactive Polls")
        print(f"   * Doubt Submission")
        print(f"   * Class Recording")
        print(f"   * Screen Sharing")
        
        # Create a notification for the class
        try:
            add_notification(
                message=f'LIVE NOW: {topic} by {teacher_name}',
                class_id=None,  # For live classes, we use the class_id directly
                target_paid_status='all',
                status='active',
                notification_type='live_class'
            )
            print(f"\nNotification Created: All students will be notified")
        except Exception as e:
            print(f"\nNote: Could not create notification - {e}")
        
        print("\n" + "=" * 60)
        print("To start the class:")
        print(f"   1. Open host page: http://localhost:10000/join-class-host/{new_class_id}")
        print(f"   2. Start your camera and go live")
        print(f"   3. Students can join at: http://localhost:10000{meeting_url}")
        print("=" * 60)
        
        return new_class_id, class_code, pin
        
    except Exception as e:
        print(f"❌ Error creating live class: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    create_demo_live_class()
