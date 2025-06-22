function joinLiveClass() {
  // You can replace this URL with your actual online class platform
  // Examples: Zoom, Google Meet, Microsoft Teams, etc.
  const classUrl = "https://meet.google.com/your-meeting-room"; // Replace with your actual meeting URL
  
  // Open the live class in a new window/tab
  window.open(classUrl, '_blank', 'width=1200,height=800,scrollbars=yes,resizable=yes');
  
  // Optional: Show a confirmation message
  alert("Opening live class session...");
}