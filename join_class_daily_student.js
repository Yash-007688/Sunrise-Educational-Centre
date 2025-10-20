// Daily.co Student Controller
class DailyStudentController {
  constructor(dailyHandler) {
    this.dailyHandler = dailyHandler;
    this.classId = null;
    this.isConnected = false;
  }

  async initialize(classId) {
    this.classId = classId;

    // Initialize Daily container
    const container = document.getElementById('dailyContainer');
    if (!container) {
      throw new Error('Daily container not found');
    }

    // Create Daily iframe
    await this.dailyHandler.createCallFrame(container, false);
    
    // Setup event handlers
    this.setupEventHandlers();
  }

  setupEventHandlers() {
    const requestHostStreamBtn = document.getElementById('requestHostStreamBtn');
    const switchToCameraBtn = document.getElementById('switchToCameraBtn');
    const switchToContentBtn2 = document.getElementById('switchToContentBtn2');
    
    if (requestHostStreamBtn) {
      requestHostStreamBtn.onclick = () => this.requestHostStream();
    }
    if (switchToCameraBtn) {
      switchToCameraBtn.onclick = () => this.switchToHostCamera();
    }
    if (switchToContentBtn2) {
      switchToContentBtn2.onclick = () => this.switchToContent();
    }

    // Handle keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === '1') {
          this.switchToContent();
        } else if (e.key === '2') {
          this.switchToHostCamera();
        }
      } else if (e.key === 'f' || e.key === 'F') {
        this.toggleFullscreen();
      }
    });
  }

  async requestHostStream() {
    try {
      // Show loading indicator
      this.showCameraLoading(true);
      
      // Update status
      this.updateStatusText('🔄 Requesting Host Camera...');
      
      // Request to join room via socket
      socket.emit('request_host_stream', {
        class_id: this.classId
      });

    } catch (error) {
      console.error('Failed to request host stream:', error);
      showNotification('Failed to request host camera', 'error');
      this.showCameraLoading(false);
    }
  }

  async joinRoom(roomUrl) {
    try {
      await this.dailyHandler.joinRoom(roomUrl, getUsername(), false);
      
      // Update UI
      this.updateConnectionUI(true);
      
      this.isConnected = true;

    } catch (error) {
      console.error('Failed to join room:', error);
      showNotification('Failed to connect to host camera', 'error');
      this.updateConnectionUI(false);
    }
  }

  switchToHostCamera() {
    if (!this.isConnected) {
      showNotification('Please wait for host camera to connect', 'warning');
      return;
    }

    const dailyContainer = document.getElementById('dailyContainer');
    const contentVideo = document.getElementById('contentVideo');
    
    if (dailyContainer && contentVideo) {
      dailyContainer.style.display = 'block';
      contentVideo.style.display = 'none';
      this.updateStatusText('🔴 Live Host Camera');
    }

    // Update buttons
    const switchToCameraBtn = document.getElementById('switchToCameraBtn');
    const switchToContentBtn2 = document.getElementById('switchToContentBtn2');
    
    if (switchToCameraBtn) switchToCameraBtn.style.display = 'none';
    if (switchToContentBtn2) switchToContentBtn2.style.display = 'inline-block';
  }

  switchToContent() {
    const dailyContainer = document.getElementById('dailyContainer');
    const contentVideo = document.getElementById('contentVideo');
    
    if (dailyContainer && contentVideo) {
      dailyContainer.style.display = 'none';
      contentVideo.style.display = 'block';
      this.updateStatusText('Watching content video');
    }

    // Update buttons
    const switchToCameraBtn = document.getElementById('switchToCameraBtn');
    const switchToContentBtn2 = document.getElementById('switchToContentBtn2');
    
    if (switchToCameraBtn && this.isConnected) switchToCameraBtn.style.display = 'inline-block';
    if (switchToContentBtn2) switchToContentBtn2.style.display = 'none';
  }

  toggleFullscreen() {
    const container = document.getElementById('dailyContainer');
    if (!container) return;

    if (!document.fullscreenElement) {
      container.requestFullscreen()
        .catch(err => {
          console.error('Error attempting to enable full-screen mode:', err);
        });
    } else {
      document.exitFullscreen();
    }
  }

  updateStatusText(text) {
    const statusText = document.getElementById('liveStatusText');
    if (statusText) {
      statusText.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          <path d="M21 3H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H3V5h18v14z"/>
        </svg>
        ${text}
      `;
    }
  }

  updateConnectionUI(isConnected) {
    const connectionStatus = document.getElementById('connectionStatus');
    if (connectionStatus) {
      connectionStatus.textContent = isConnected ? '🔴 Live' : '⚪ Disconnected';
      connectionStatus.style.background = isConnected ? 'rgba(72,187,120,0.9)' : 'rgba(229,62,62,0.9)';
    }

    const requestBtn = document.getElementById('requestHostStreamBtn');
    const switchToCameraBtn = document.getElementById('switchToCameraBtn');
    const switchToContentBtn2 = document.getElementById('switchToContentBtn2');
    
    if (requestBtn) requestBtn.style.display = isConnected ? 'none' : 'inline-block';
    if (switchToCameraBtn) switchToCameraBtn.style.display = 'none';
    if (switchToContentBtn2) switchToContentBtn2.style.display = isConnected ? 'inline-block' : 'none';
  }

  showCameraLoading(show) {
    const loadingIndicator = document.getElementById('cameraLoading');
    if (loadingIndicator) {
      loadingIndicator.style.display = show ? 'block' : 'none';
    }
  }
}