import os
import requests
from flask import jsonify
from datetime import datetime, timedelta

class DailyHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_base = 'https://api.daily.co/v1'
        self.rooms = {}  # Store active room info

    def create_room(self, class_id):
        """Create a new Daily.co room for a live class"""
        try:
            # Room configuration
            room_config = {
                'name': f'live-class-{class_id}',
                'properties': {
                    'max_participants': 100,
                    'enable_chat': True,
                    'enable_recording': True,
                    'enable_knocking': False,
                    'enable_screenshare': True,
                    'start_video_off': True,
                    'start_audio_off': True,
                    'exp': int((datetime.now() + timedelta(hours=24)).timestamp())  # 24-hour expiry
                }
            }

            # Make API request to create room
            response = requests.post(
                f'{self.api_base}/rooms',
                json=room_config,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            )
            response.raise_for_status()
            room_data = response.json()

            # Store room info
            self.rooms[class_id] = {
                'url': room_data['url'],
                'name': room_data['name'],
                'created_at': datetime.now().isoformat()
            }

            return jsonify({
                'success': True,
                'room_url': room_data['url'],
                'message': 'Daily.co room created successfully'
            })

        except requests.exceptions.RequestException as e:
            print(f'Error creating Daily.co room: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Failed to create Daily.co room',
                'message': str(e)
            }), 500

    def get_room(self, class_id):
        """Get Daily.co room info for a live class"""
        try:
            if class_id not in self.rooms:
                # Try to fetch room info from Daily.co
                response = requests.get(
                    f'{self.api_base}/rooms/live-class-{class_id}',
                    headers={'Authorization': f'Bearer {self.api_key}'}
                )
                
                if response.status_code == 200:
                    room_data = response.json()
                    self.rooms[class_id] = {
                        'url': room_data['url'],
                        'name': room_data['name'],
                        'created_at': room_data.get('created_at')
                    }
                    return jsonify({
                        'success': True,
                        'room_url': room_data['url']
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Room not found'
                    }), 404

            return jsonify({
                'success': True,
                'room_url': self.rooms[class_id]['url']
            })

        except requests.exceptions.RequestException as e:
            print(f'Error getting Daily.co room: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Failed to get Daily.co room info',
                'message': str(e)
            }), 500

    def delete_room(self, class_id):
        """Delete a Daily.co room when class ends"""
        try:
            if class_id in self.rooms:
                room_name = f'live-class-{class_id}'
                response = requests.delete(
                    f'{self.api_base}/rooms/{room_name}',
                    headers={'Authorization': f'Bearer {self.api_key}'}
                )
                response.raise_for_status()
                
                # Remove room from local storage
                del self.rooms[class_id]
                
                return jsonify({
                    'success': True,
                    'message': 'Room deleted successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Room not found'
                }), 404

        except requests.exceptions.RequestException as e:
            print(f'Error deleting Daily.co room: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Failed to delete Daily.co room',
                'message': str(e)
            }), 500

    def start_recording(self, class_id):
        """Start recording a Daily.co room"""
        try:
            if class_id not in self.rooms:
                return jsonify({
                    'success': False,
                    'error': 'Room not found'
                }), 404

            response = requests.post(
                f'{self.api_base}/recordings/start',
                json={'room_name': f'live-class-{class_id}'},
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            response.raise_for_status()

            return jsonify({
                'success': True,
                'message': 'Recording started'
            })

        except requests.exceptions.RequestException as e:
            print(f'Error starting recording: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Failed to start recording',
                'message': str(e)
            }), 500

    def stop_recording(self, class_id):
        """Stop recording a Daily.co room"""
        try:
            if class_id not in self.rooms:
                return jsonify({
                    'success': False,
                    'error': 'Room not found'
                }), 404

            response = requests.post(
                f'{self.api_base}/recordings/stop',
                json={'room_name': f'live-class-{class_id}'},
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            response.raise_for_status()

            return jsonify({
                'success': True,
                'message': 'Recording stopped'
            })

        except requests.exceptions.RequestException as e:
            print(f'Error stopping recording: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Failed to stop recording',
                'message': str(e)
            }), 500

# Initialize Daily handler with API key
daily_handler = DailyHandler(os.getenv('DAILY_API_KEY'))