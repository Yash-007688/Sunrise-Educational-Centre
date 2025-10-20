// Daily.co Host Controller
class DailyHostController {
  constructor(dailyHandler) {
    this.dailyHandler = dailyHandler;
    this.classId = null;
    this.isStreaming = false;
  }

  async initialize(classId) {
    this.classId = classId;

    // Initialize Daily container
    const container = document.getElementById('dailyContainer');
    if (!container) {
      throw new Error('Daily container not found');
    }

    // Create Daily iframe
    await this.dailyHandler.createCallFrame(container, true);
    
    // Setup UI event handlers
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    // Camera controls
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const toggleMicBtn = document.getElementById('toggleMicBtn');
    
    if (startCameraBtn) {
      startCameraBtn.onclick = () => this.startStream();
    }
    if (stopCameraBtn) {
      stopCameraBtn.onclick = () => this.stopStream();
    }
    if (toggleMicBtn) {
      toggleMicBtn.onclick = () => this.toggleMic();
    }

    // Video mode controls
    const showCameraBtn = document.getElementById('showCameraBtn');
    const showContentBtn = document.getElementById('showContentBtn');
    
    if (showCameraBtn) {
      showCameraBtn.onclick = () => this.showCamera();
    }
    if (showContentBtn) {
      showContentBtn.onclick = () => this.showContent();
    }
  }

  async startStream() {
    try {
      // Create Daily room if not exists
      if (!this.dailyHandler.roomUrl) {
        await this.dailyHandler.createRoom(this.classId);
      }

      // Join room as host
      await this.dailyHandler.joinRoom(this.dailyHandler.roomUrl, 'Host', true);
      
      // Update UI
      this.updateStreamUI(true);
      
      // Emit socket event
      socket.emit('host_stream_ready', {
        class_id: this.classId,
        room_url: this.dailyHandler.roomUrl
      });

      this.isStreaming = true;

    } catch (error) {
      console.error('Failed to start stream:', error);
      showNotification('Failed to start camera stream', 'error');
    }
  }

  async stopStream() {
    try {
      await this.dailyHandler.leaveRoom();
      
      // Update UI
      this.updateStreamUI(false);
      
      // Emit socket event
      socket.emit('host_camera_status', {
        class_id: this.classId,
        status: 'offline',
        message: 'Host camera is offline'
      });

      this.isStreaming = false;

    } catch (error) {
      console.error('Failed to stop stream:', error);
      showNotification('Failed to stop camera stream', 'error');
    }
  }

  async toggleMic() {
    try {
      await this.dailyHandler.toggleAudio();
      const isMuted = !(await this.dailyHandler.callFrame.localAudio());
      
      // Update UI
      const toggleMicBtn = document.getElementById('toggleMicBtn');
      if (toggleMicBtn) {
        if (isMuted) {
          toggleMicBtn.classList.add('muted');
          toggleMicBtn.title = 'Unmute Microphone';
        } else {
          toggleMicBtn.classList.remove('muted');
          toggleMicBtn.title = 'Mute Microphone';
        }
      }
      
      // Emit socket event
      socket.emit('host_mic_status', {
        class_id: this.classId,
        muted: isMuted
      });

    } catch (error) {
      console.error('Failed to toggle microphone:', error);
      showNotification('Failed to toggle microphone', 'error');
    }
  }

  showCamera() {
    if (!this.isStreaming) {
      showNotification('Please start the camera first', 'warning');
      return;
    }

    const dailyContainer = document.getElementById('dailyContainer');
    const contentVideo = document.getElementById('contentVideo');
    const showCameraBtn = document.getElementById('showCameraBtn');
    const showContentBtn = document.getElementById('showContentBtn');

    if (dailyContainer && contentVideo) {
      dailyContainer.style.display = 'block';
      contentVideo.style.display = 'none';
    }

    if (showCameraBtn) showCameraBtn.classList.add('active');
    if (showContentBtn) showContentBtn.classList.remove('active');

    socket.emit('host_video_mode', {
      class_id: this.classId,
      mode: 'camera',
      message: 'Host is showing live camera'
    });
  }

  showContent() {
    const dailyContainer = document.getElementById('dailyContainer');
    const contentVideo = document.getElementById('contentVideo');
    const showCameraBtn = document.getElementById('showCameraBtn');
    const showContentBtn = document.getElementById('showContentBtn');

    if (dailyContainer && contentVideo) {
      dailyContainer.style.display = 'none';
      contentVideo.style.display = 'block';
    }

    if (showCameraBtn) showCameraBtn.classList.remove('active');
    if (showContentBtn) showContentBtn.classList.add('active');

    socket.emit('host_video_mode', {
      class_id: this.classId,
      mode: 'content',
      message: 'Host is showing content video'
    });
  }

  updateStreamUI(isStreaming) {
    // Update button visibility
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    if (startCameraBtn) startCameraBtn.style.display = isStreaming ? 'none' : 'inline-block';
    if (stopCameraBtn) stopCameraBtn.style.display = isStreaming ? 'inline-block' : 'none';
    
    // Update status text
    const statusText = document.getElementById('statusText');
    if (statusText) {
      statusText.textContent = isStreaming ? 'Camera Active - Live Class Ready' : 'Camera Off - Ready to Start Live Class';
    }
    
    // Update device status
    const deviceStatus = document.getElementById('deviceStatus');
    if (deviceStatus) {
      deviceStatus.innerHTML = isStreaming ? '🔴 Live streaming active' : '📱 Ready to start streaming';
    }
  }

  async startRecording() {
    try {
      await this.dailyHandler.startRecording();
      showNotification('Recording started', 'success');
      
      socket.emit('recording_started', {
        class_id: this.classId
      });

    } catch (error) {
      console.error('Failed to start recording:', error);
      showNotification('Failed to start recording', 'error');
    }
  }

  async stopRecording() {
    try {
      await this.dailyHandler.stopRecording();
      showNotification('Recording stopped', 'success');
      
      socket.emit('recording_stopped', {
        class_id: this.classId
      });

    } catch (error) {
      console.error('Failed to stop recording:', error);
      showNotification('Failed to stop recording', 'error');
    }
  }
}