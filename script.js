function joinLiveClass() {
  // Navigate to the dedicated online class page
  window.location.href = 'online-class.html';
}

// Typing animation for the main heading
document.addEventListener('DOMContentLoaded', function() {
  const headingElement = document.getElementById('typing-heading');
  const text = "Expert Coaching for Class 9 to 12";
  let index = 0;
  
  headingElement.classList.add('typing-active');
  
  function typeText() {
    if (index < text.length) {
      headingElement.textContent += text.charAt(index);
      index++;
      setTimeout(typeText, 100); // Adjust speed here (100ms per character)
    } else {
      // Remove typing cursor after completion
      setTimeout(() => {
        headingElement.style.borderRight = 'none';
      }, 1000);
    }
  }
  
  // Start typing after a small delay
  setTimeout(typeText, 500);
});