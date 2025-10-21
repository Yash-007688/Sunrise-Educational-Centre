"""
Small test script to create a temporary Daily.co room using the DAILY_API_KEY from the environment.
Run only when you want to test the API key. This script will actually call Daily.co REST API.
Usage (PowerShell):
    python test_daily_room.py

Note: Ensure you have set DAILY_API_KEY in your environment or in a .env file (do NOT commit your .env).
"""
import os
import requests
import sys
from datetime import datetime, timedelta

API_KEY = os.getenv('DAILY_API_KEY')
if not API_KEY:
    print('DAILY_API_KEY environment variable is not set. Aborting.')
    sys.exit(1)

API_BASE = 'https://api.daily.co/v1'

room_name = f'test-room-{int(datetime.now().timestamp())}'
room_payload = {
    'name': room_name,
    'properties': {
        'enable_chat': True,
        'enable_recording': False,
        'start_video_off': False,
        'start_audio_off': False,
        'exp': int((datetime.now() + timedelta(hours=1)).timestamp())
    }
}

print('Creating room...', room_name)
resp = requests.post(f'{API_BASE}/rooms', json=room_payload, headers={'Authorization': f'Bearer {API_KEY}'})
if resp.status_code not in (200, 201):
    print('Failed to create room', resp.status_code, resp.text)
    sys.exit(2)

room = resp.json()
print('Room created:', room.get('url'))

# Cleanup: delete the room
print('Deleting room...', room_name)
resp2 = requests.delete(f"{API_BASE}/rooms/{room_name}", headers={'Authorization': f'Bearer {API_KEY}'})
if resp2.status_code not in (200, 204):
    print('Failed to delete room', resp2.status_code, resp2.text)
    sys.exit(3)

print('Test complete. Room created and deleted successfully.')