from datetime import datetime
from typing import Callable, Optional, Dict, Any


class LiveClassManager:
    """
    Manages realtime features for the online class:
    - Chat (public/private/locked) and history sync
    - Poll creation and voting
    - Doubt submission and updates
    - WebRTC camera signaling (offer/answer/ice) and host status

    Usage:
        manager = LiveClassManager(get_db=get_db)
        manager.register_handlers(socketio)
    """

    def __init__(self, get_db: Callable[[], Any]):
        self.get_db = get_db

    # =====================
    # Registration
    # =====================
    def register_handlers(self, socketio):
        """Register all Socket.IO event handlers on the provided socketio instance."""

        # --------------- Chat ---------------
        @socketio.on('chat_message')
        def handle_chat_message(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                user_id = data.get('user_id')
                username = data.get('username', 'Anonymous')
                message = data.get('message')
                message_type = data.get('type', 'chat')

                if not class_id or not message:
                    socketio.emit('error', {'message': 'Invalid chat data'})
                    return

                db = self.get_db()
                c = db.cursor()
                c.execute(
                    '''INSERT INTO live_class_messages (class_id, user_id, username, message, message_type, created_at)
                       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                    (class_id, user_id, username, message, message_type)
                )
                db.commit()

                message_data = {
                    'id': c.lastrowid,
                    'class_id': class_id,
                    'user_id': user_id,
                    'username': username,
                    'message': message,
                    'message_type': message_type,
                    'created_at': datetime.now().isoformat(),
                }

                # Debug: log where message is being emitted
                print(f"[LiveClassManager] chat_message from {user_id} in class {class_id} -> broadcasting to room liveclass_{class_id}")
                socketio.emit('new_chat_message', message_data, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] chat_message error: {e}")
                socketio.emit('error', {'message': 'Failed to send message'})

        @socketio.on('get_chat_messages')
        def handle_get_chat_messages(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                limit = int(data.get('limit') or 50)
                db = self.get_db()
                c = db.cursor()
                c.execute(
                    '''SELECT id, class_id, user_id, username, message, message_type, created_at
                       FROM live_class_messages WHERE class_id=? ORDER BY id DESC LIMIT ?''',
                    (class_id, limit)
                )
                rows = c.fetchall() or []
                # Return oldest-first for UI rendering
                rows.reverse()
                messages = [
                    {
                        'id': r[0], 'class_id': r[1], 'user_id': r[2], 'username': r[3],
                        'message': r[4], 'message_type': r[5], 'created_at': r[6]
                    }
                    for r in rows
                ]
                socketio.emit('chat_messages_history', {'class_id': class_id, 'messages': messages})
            except Exception as e:
                print(f"[LiveClassManager] get_chat_messages error: {e}")
                socketio.emit('error', {'message': 'Failed to load chat history'})

        @socketio.on('chat_status_change')
        def handle_chat_status_change(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                status = data.get('status')  # locked | unlocked | private | public
                message = data.get('message')
                if not class_id or not status:
                    socketio.emit('error', {'message': 'Invalid chat status data'})
                    return
                payload = {'class_id': class_id, 'status': status, 'message': message}
                socketio.emit('chat_status_change', payload, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] chat_status_change error: {e}")
                socketio.emit('error', {'message': 'Failed to change chat status'})

        @socketio.on('chat_cleared')
        def handle_chat_cleared(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                if not class_id:
                    return
                db = self.get_db()
                c = db.cursor()
                c.execute('DELETE FROM live_class_messages WHERE class_id=?', (class_id,))
                db.commit()
                socketio.emit('chat_cleared', {'class_id': class_id}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] chat_cleared error: {e}")

        # --------------- WebRTC / Camera ---------------
        @socketio.on('webrtc_offer')
        def handle_webrtc_offer(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                offer = data.get('offer')
                from_user = data.get('from_user')
                if class_id and offer:
                    print(f"[LiveClassManager] webrtc_offer from {from_user} for class {class_id}")
                    socketio.emit('webrtc_offer', {'offer': offer, 'from_user': from_user}, room=f'liveclass_{class_id}', skip_sid=None)
            except Exception as e:
                print(f"[LiveClassManager] webrtc_offer error: {e}")

        @socketio.on('webrtc_answer')
        def handle_webrtc_answer(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                answer = data.get('answer')
                to_user = data.get('to_user')
                if class_id and answer:
                    print(f"[LiveClassManager] webrtc_answer to {to_user} for class {class_id}")
                    socketio.emit('webrtc_answer', {'answer': answer, 'from_user': 'host', 'to_user': to_user}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] webrtc_answer error: {e}")

        @socketio.on('webrtc_ice_candidate')
        def handle_webrtc_ice(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                candidate = data.get('candidate')
                from_user = data.get('from_user')
                if class_id and candidate:
                    print(f"[LiveClassManager] webrtc_ice_candidate from {from_user} for class {class_id}")
                    socketio.emit('webrtc_ice_candidate', {'candidate': candidate, 'from_user': from_user}, room=f'liveclass_{class_id}', skip_sid=None)
            except Exception as e:
                print(f"[LiveClassManager] webrtc_ice_candidate error: {e}")

        @socketio.on('host_camera_status')
        def handle_host_camera_status(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                status = data.get('status')  # live | offline
                message = data.get('message')
                if class_id and status:
                    socketio.emit('host_camera_status', {'class_id': class_id, 'status': status, 'message': message}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] host_camera_status error: {e}")

        @socketio.on('host_video_mode')
        def handle_host_video_mode(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                mode = data.get('mode')  # camera | content
                message = data.get('message', 'Watching content video')
                if class_id and mode:
                    socketio.emit('host_video_mode', {'class_id': class_id, 'mode': mode, 'message': message}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] host_video_mode error: {e}")

        @socketio.on('host_mic_status')
        def handle_host_mic_status(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                muted = bool(data.get('muted'))
                socketio.emit('host_mic_status', {'class_id': class_id, 'muted': muted}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] host_mic_status error: {e}")

        # --------------- Polls & Doubts ---------------
        @socketio.on('get_polls_and_doubts')
        def handle_get_polls_and_doubts(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                db = self.get_db()
                c = db.cursor()

                c.execute('''SELECT id, question FROM polls WHERE class_id=? ORDER BY id DESC''', (class_id,))
                polls = [{'id': r[0], 'question': r[1], 'options': self._load_poll_options(c, r[0])} for r in (c.fetchall() or [])]

                c.execute('''SELECT id, user_id, username, doubt_text, status FROM doubts WHERE class_id=? ORDER BY id DESC''', (class_id,))
                doubts = [{'id': r[0], 'user_id': r[1], 'username': r[2], 'doubt_text': r[3], 'status': r[4]} for r in (c.fetchall() or [])]

                socketio.emit('init_polls_and_doubts', {'class_id': class_id, 'polls': polls, 'doubts': doubts})
            except Exception as e:
                print(f"[LiveClassManager] get_polls_and_doubts error: {e}")

        @socketio.on('new_poll')
        def handle_new_poll(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                question = data.get('question')
                options = data.get('options') or []
                if not class_id or not question or not options:
                    socketio.emit('error', {'message': 'Invalid poll data'})
                    return
                db = self.get_db()
                c = db.cursor()
                c.execute('INSERT INTO polls (class_id, question, created_at) VALUES (?,?,CURRENT_TIMESTAMP)', (class_id, question))
                poll_id = c.lastrowid
                for opt in options:
                    c.execute('INSERT INTO poll_options (poll_id, option_text) VALUES (?,?)', (poll_id, opt))
                db.commit()
                socketio.emit('new_poll', {'id': poll_id, 'class_id': class_id, 'question': question}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] new_poll error: {e}")

        @socketio.on('vote_poll')
        def handle_vote_poll(data: Dict[str, Any]):
            try:
                poll_id = data.get('poll_id')
                option_id = data.get('option_id')
                class_id = data.get('class_id')
                user_id = data.get('user_id')
                if not poll_id or not option_id or not class_id:
                    return
                db = self.get_db()
                c = db.cursor()
                c.execute('INSERT INTO poll_votes (poll_id, option_id, user_id, created_at) VALUES (?,?,?,CURRENT_TIMESTAMP)', (poll_id, option_id, user_id))
                db.commit()
                # Broadcast updated results
                results = self._compute_poll_results(c, poll_id)
                socketio.emit('poll_results', {'poll_id': poll_id, 'results': results}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] vote_poll error: {e}")

        @socketio.on('submit_doubt')
        def handle_submit_doubt(data: Dict[str, Any]):
            try:
                class_id = data.get('class_id')
                user_id = data.get('user_id')
                username = data.get('username')
                doubt_text = data.get('doubt_text')
                if not class_id or not doubt_text:
                    return
                db = self.get_db()
                c = db.cursor()
                c.execute('INSERT INTO doubts (class_id, user_id, username, doubt_text, status, created_at) VALUES (?,?,?,?,?,CURRENT_TIMESTAMP)', (class_id, user_id, username, doubt_text, 'open'))
                db.commit()
                socketio.emit('update_doubts', {'class_id': class_id, 'doubts': self._load_doubts(c, class_id)}, room=f'liveclass_{class_id}')
            except Exception as e:
                print(f"[LiveClassManager] submit_doubt error: {e}")

    # =====================
    # Helpers
    # =====================
    def _load_poll_options(self, cursor, poll_id: int):
        cursor.execute('SELECT id, option_text FROM poll_options WHERE poll_id=? ORDER BY id', (poll_id,))
        return [{'id': r[0], 'option_text': r[1]} for r in (cursor.fetchall() or [])]

    def _compute_poll_results(self, cursor, poll_id: int):
        cursor.execute('''
            SELECT po.id, po.option_text, COUNT(pv.id) as votes
            FROM poll_options po
            LEFT JOIN poll_votes pv ON pv.option_id = po.id
            WHERE po.poll_id=?
            GROUP BY po.id, po.option_text
            ORDER BY po.id
        ''', (poll_id,))
        return [{'option_id': r[0], 'option_text': r[1], 'votes': r[2]} for r in (cursor.fetchall() or [])]

    def _load_doubts(self, cursor, class_id: int):
        cursor.execute('SELECT id, user_id, username, doubt_text, status FROM doubts WHERE class_id=? ORDER BY id DESC', (class_id,))
        return [
            {'id': r[0], 'user_id': r[1], 'username': r[2], 'doubt_text': r[3], 'status': r[4]}
            for r in (cursor.fetchall() or [])
        ]


