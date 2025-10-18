# 📹 Live Class Camera Testing Guide

## 🎯 Test Objective
Verify that the host camera streams correctly to student view using WebRTC.

---

## 🔧 Prerequisites

✅ **Server Running:** http://localhost:10000  
✅ **User Created:** `yash` (password: `yash`, role: student)  
✅ **Live Class Created:** Class ID 2, Code: `307423`  
✅ **Debug Logging:** Enhanced logs enabled on both pages

---

## 📝 Step-by-Step Testing Instructions

### **STEP 1: Open Host Page (Teacher/Admin)**

1. Open a browser (Chrome/Edge recommended)
2. Navigate to: `http://localhost:10000/join-class-host/2`
3. Press `F12` to open Developer Console
4. Look for these console logs:
   ```
   [Host] ✅ Joined room successfully: liveclass_2
   [Host] Session ID: <socket_id>
   ```

### **STEP 2: Start Camera on Host Page**

1. Click the **"Start Camera"** button (camera icon)
2. Grant browser permissions when prompted:
   - ✅ Allow Camera
   - ✅ Allow Microphone
3. **Expected Result:**
   - Your camera feed appears in the video preview
   - Button changes to "Stop Camera"
   - Status shows "🔴 Live - Camera Active"
4. **Console Logs to Watch For:**
   ```
   [Host] Camera started successfully
   [Host] Local stream ready
   Broadcasting host_camera_status to room 'liveclass_2'
   ```

### **STEP 3: Open Student Page (in Different Browser/Incognito)**

1. Open a **NEW BROWSER WINDOW** or **INCOGNITO MODE**
2. Navigate to: `http://localhost:10000`
3. Login as:
   - Username: `yash`
   - Password: `yash`
4. After login, go to: `http://localhost:10000/join-class/307423`
5. Press `F12` to open Developer Console
6. Look for these console logs:
   ```
   [Student] ✅ Joined room successfully: liveclass_2
   [Student] Session ID: <socket_id>
   ```

### **STEP 4: Request Host Camera Stream (Student Side)**

1. On the student page, click **"Request Host Camera"** button
2. **Expected Result:**
   - Status changes to "🔄 Requesting Host Camera..."
   - Loading spinner appears
3. **Console Logs to Watch For (Student):**
   ```
   [Student] Requesting host stream
   [Student] ✅ webrtc_offer emitted to server
   WebRTC initialized for receiving host stream
   ```
4. **Console Logs to Watch For (Host):**
   ```
   [Host] Received webrtc_offer
   [Host] Processing offer from student <user_id>
   [Host] Creating peer connection for student
   [Host] Adding local stream to peer connection
   ```

### **STEP 5: Verify Video Stream Connection**

**On Student Page:**
1. **Expected Result:**
   - Host camera feed should appear in ~3-10 seconds
   - Status shows "🔴 Live Host Camera"
   - Video quality indicator shows connection strength
2. **Console Logs to Watch For:**
   ```
   Received host stream: MediaStream
   Connection state: connected
   🔴 Live
   Host camera stream connected successfully
   ```

**On Host Page:**
1. **Console Logs to Watch For:**
   ```
   [Host] Peer connection established for student <user_id>
   [Host] ICE connection state: connected
   ```

---

## 🐛 Troubleshooting Guide

### **Issue: Camera doesn't start on host page**

**Possible Causes:**
- Browser doesn't have camera permissions
- Camera is being used by another application
- HTTPS required (localhost should work)

**Solutions:**
1. Check browser permissions: `Settings → Privacy → Camera`
2. Close other apps using camera (Zoom, Teams, etc.)
3. Try a different browser
4. Check console for error messages

**Console Debug Commands:**
```javascript
// Check if camera is accessible
navigator.mediaDevices.enumerateDevices()
  .then(devices => console.log('Devices:', devices.filter(d => d.kind === 'videoinput')))

// Check permissions
navigator.permissions.query({name: 'camera'})
  .then(result => console.log('Camera permission:', result.state))
```

---

### **Issue: Student doesn't receive host stream**

**Possible Causes:**
- Room join failed (not in same room)
- WebRTC offer not reaching host
- Firewall blocking WebRTC
- ICE candidate exchange failing

**Solutions:**

1. **Verify Room Join:**
   - Both pages should show: `Joined room successfully: liveclass_2`
   - Room name must match exactly

2. **Check Backend Logs:**
   - Look in server console for:
     ```
     [WebRTC] Received webrtc_offer for class 2
     [WebRTC] Broadcasting to room 'liveclass_2'
     ```

3. **Verify WebRTC Events:**
   - Student Console:
     ```javascript
     // Check if WebRTC events are being received
     socket.on('webrtc_answer', data => console.log('Got answer:', data))
     socket.on('webrtc_ice_candidate', data => console.log('Got ICE:', data))
     ```

4. **Check Network:**
   - Ensure both pages can access STUN servers
   - Check firewall settings
   - Try disabling antivirus temporarily

---

### **Issue: Video is black or frozen**

**Possible Causes:**
- Camera not properly initialized
- Codec mismatch
- Bandwidth issues
- Track not being sent

**Solutions:**

1. **Check Video Track Status (Host):**
   ```javascript
   // In host page console
   if (localStream) {
     localStream.getVideoTracks().forEach(track => {
       console.log('Track:', track.label, 'Enabled:', track.enabled, 'Ready:', track.readyState)
     })
   }
   ```

2. **Check Remote Stream (Student):**
   ```javascript
   // In student page console
   const video = document.getElementById('hostCameraFeed')
   console.log('Video:', video.srcObject, 'Paused:', video.paused, 'Ready:', video.readyState)
   ```

3. **Restart Both Sides:**
   - Host: Stop camera → Start camera
   - Student: Refresh page → Request host camera

---

### **Issue: Room participants = 0**

**Possible Causes:**
- Backend not tracking room joins
- Socket.IO connection issues
- Room name mismatch

**Solutions:**

1. **Check Backend Room Tracking:**
   - Server console should show:
     ```
     Client <socket_id> joined room liveclass_2
     [Chat] Room has 2 participants: [<sid1>, <sid2>]
     ```

2. **Verify Socket Connection:**
   ```javascript
   // In browser console
   console.log('Connected:', socket.connected, 'ID:', socket.id)
   ```

3. **Force Rejoin:**
   ```javascript
   // In browser console
   socket.emit('join-room', { room: 'liveclass_2' })
   ```

---

## 📊 Expected Console Output Summary

### **Host Page (Successful Connection):**
```
[Host] ✅ Joined room successfully: liveclass_2
[Host] Camera started successfully
[Host] Local stream ready: MediaStream {id: "...", active: true}
[Host] Received webrtc_offer: {from_user: "4", to_user: "host", ...}
[Host] Processing offer from student 4
[Host] Creating peer connection for student 4
[Host] Adding local stream to peer connection
[Host] Sending answer to student 4
[Host] ICE connection state: connected
```

### **Student Page (Successful Connection):**
```
[Student] ✅ Joined room successfully: liveclass_2
[Student] Requesting host stream
[Student] ✅ webrtc_offer emitted to server
WebRTC initialized for receiving host stream
Received webrtc_answer: {from_user: "host", answer: {...}}
Set host answer
Added host ICE candidate
Received host stream: MediaStream {id: "...", active: true}
Connection state: connected
Host camera stream connected successfully
```

---

## ✅ Success Criteria

- [ ] Host camera starts and shows preview
- [ ] Student can join the room
- [ ] Student can request host camera
- [ ] Video stream appears on student page within 10 seconds
- [ ] Video is clear and not frozen
- [ ] Both consoles show "connected" status
- [ ] Chat, polls, and doubts work simultaneously

---

## 🎥 Testing Chat/Polls/Doubts While Streaming

Once camera is working, test real-time features:

### **Test Chat:**
1. **Host:** Send message → Check student receives it
2. **Student:** Send message → Check host receives it
3. **Console:** Look for `[Chat] 📩 Received new_chat_message event`

### **Test Polls:**
1. **Host:** Create a poll with 2+ options
2. **Student:** Should see poll appear automatically
3. **Student:** Vote on poll
4. **Host:** See results update in real-time
5. **Console:** Look for `[Poll] 📩 Received new_poll event`

### **Test Doubts:**
1. **Student:** Submit a doubt
2. **Host:** Should see doubt appear in Doubts tab
3. **Host:** Resolve or ignore the doubt
4. **Student:** See status update
5. **Console:** Look for `[Doubt] 📩 Received update_doubts event`

---

## 📞 Quick Test Commands

Copy these into browser console for quick testing:

**Check Room Status:**
```javascript
console.log('Room:', room, 'Joined:', joinedRoom, 'Connected:', isConnected)
```

**Force Send Test Message:**
```javascript
socket.emit('chat_message', {
  class_id: classId,
  user_id: getUserId(),
  username: getUsername(),
  message: 'Test message from console',
  type: 'chat'
})
```

**Check WebRTC Status:**
```javascript
if (peerConnection) {
  console.log('Connection:', peerConnection.connectionState)
  console.log('ICE:', peerConnection.iceConnectionState)
  console.log('Signaling:', peerConnection.signalingState)
}
```

---

## 🎯 What to Report Back

After testing, report:

1. ✅/❌ Camera started on host page
2. ✅/❌ Student received video stream
3. ✅/❌ Chat messages synced
4. ✅/❌ Polls appeared on both pages
5. ✅/❌ Doubts synced correctly
6. 📋 Any console errors or warnings
7. ⏱️ Time taken for video to appear

---

**Good luck with testing! 🚀**
