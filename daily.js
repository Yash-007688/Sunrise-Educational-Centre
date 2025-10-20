// Daily.co integration
const DAILY_API_KEY = 'YOUR_DAILY_API_KEY_HERE'; // Replace with actual API key

class DailyHandler {
  constructor() {
    this.callFrame = null;
    this.roomUrl = null;
  }

  // Initialize Daily iframe 
  async createCallFrame(containerElement, isHost = false) {
    if (!containerElement) return null;
    
    // Create Daily iframe
    this.callFrame = window.DailyIframe.createFrame(containerElement, {
      iframeStyle: {
        width: '100%',
        height: '100%',
        border: '0',
        borderRadius: '12px'
      },
      showLeaveButton: true,
      showFullscreenButton: true
    });

    // Add event handlers
    this.callFrame
      .on('joining-meeting', () => {
        console.log('Joining Daily meeting...');
      })
      .on('joined-meeting', () => {
        console.log('Joined Daily meeting');
      })
      .on('left-meeting', () => {
        console.log('Left Daily meeting');
      })
      .on('participant-joined', (event) => {
        console.log('Participant joined:', event.participant);
      })
      .on('participant-left', (event) => {
        console.log('Participant left:', event.participant);
      })
      .on('error', (event) => {
        console.error('Daily error:', event);
      });

    return this.callFrame;
  }

  // Create a new Daily room for a class
  async createRoom(classId) {
    try {
      const response = await fetch('https://api.daily.co/v1/rooms', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${DAILY_API_KEY}`
        },
        body: JSON.stringify({
          name: `live-class-${classId}`,
          properties: {
            max_participants: 100,
            enable_chat: true,
            enable_recording: true,
            enable_knocking: false,
            enable_screenshare: true,
            start_video_off: true,
            start_audio_off: true
          }
        })
      });

      const data = await response.json();
      this.roomUrl = data.url;
      return data.url;

    } catch (error) {
      console.error('Error creating Daily room:', error);
      throw error;
    }
  }

  // Join a Daily room
  async joinRoom(roomUrl, username, isHost = false) {
    if (!this.callFrame) {
      throw new Error('Call frame not initialized');
    }

    try {
      await this.callFrame.join({
        url: roomUrl,
        userName: username,
        showLeaveButton: true,
        showFullscreenButton: true,
        showLocalVideo: isHost,
        showParticipantsBar: isHost
      });

    } catch (error) {
      console.error('Error joining Daily room:', error);
      throw error;
    }
  }

  // Leave the Daily room
  async leaveRoom() {
    if (this.callFrame) {
      await this.callFrame.leave();
    }
  }

  // Toggle local video
  async toggleVideo() {
    if (this.callFrame) {
      await this.callFrame.setLocalVideo(!await this.callFrame.localVideo());
    }
  }

  // Toggle local audio
  async toggleAudio() {
    if (this.callFrame) {
      await this.callFrame.setLocalAudio(!await this.callFrame.localAudio());
    }
  }

  // Start recording
  async startRecording() {
    if (this.callFrame) {
      try {
        await this.callFrame.startRecording();
      } catch (error) {
        console.error('Error starting recording:', error);
        throw error;
      }
    }
  }

  // Stop recording
  async stopRecording() {
    if (this.callFrame) {
      try {
        await this.callFrame.stopRecording();
      } catch (error) {
        console.error('Error stopping recording:', error);
        throw error;
      }
    }
  }
}

// Export Daily handler instance
window.DailyHandler = DailyHandler;