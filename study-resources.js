
// Study Resources Page JavaScript

// Tab switching functionality
function showClass(className) {
  // Hide all class content
  const allContent = document.querySelectorAll('.class-content');
  allContent.forEach(content => {
    content.classList.remove('active');
  });
  
  // Remove active class from all buttons
  const allButtons = document.querySelectorAll('.tab-button');
  allButtons.forEach(button => {
    button.classList.remove('active');
  });
  
  // Show selected class content
  document.getElementById(className).classList.add('active');
  
  // Add active class to clicked button
  event.target.classList.add('active');
}

// Resource opening functionality
function openResource(resourceName) {
  // This would typically open a PDF or document
  // For now, we'll show an alert with the resource name
  alert(`Opening: ${resourceName}\n\nThis would typically open the PDF/document in a new tab or download it.`);
  
  // In a real implementation, you might do something like:
  // window.open(`resources/${resourceName.replace(/\s+/g, '_')}.pdf`, '_blank');
}

// Quick access functions
function downloadApp() {
  alert('Mobile app download would start here.\n\nRedirecting to app store...');
  // In real implementation:
  // window.open('https://play.google.com/store/apps/your-app', '_blank');
}

function openVideoLibrary() {
  alert('Opening video library...\n\nThis would redirect to the video lectures section.');
  // In real implementation:
  // window.location.href = 'video-library.html';
}

function submitDoubt() {
  const doubt = prompt('Please enter your doubt or question:');
  if (doubt && doubt.trim()) {
    alert(`Your doubt has been submitted successfully!\n\nDoubt: "${doubt}"\n\nEr. Mohit Nariyani will respond within 24 hours.`);
    
    // In real implementation, you would send this to a server:
    // submitDoubtToServer(doubt);
  }
}

// Search functionality (bonus feature)
function searchResources() {
  const searchTerm = document.getElementById('searchInput').value.toLowerCase();
  const resourceCards = document.querySelectorAll('.resource-card');
  
  resourceCards.forEach(card => {
    const cardText = card.textContent.toLowerCase();
    if (cardText.includes(searchTerm)) {
      card.style.display = 'block';
      card.style.opacity = '1';
    } else {
      card.style.display = 'none';
      card.style.opacity = '0.5';
    }
  });
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
  // Add search functionality if search input exists
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {
    searchInput.addEventListener('input', searchResources);
  }
  
  // Add click tracking for analytics (optional)
  const resourceLinks = document.querySelectorAll('.resource-card a');
  resourceLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Track which resources are most accessed
      console.log(`Resource accessed: ${this.textContent}`);
    });
  });
  
  // Auto-save user's last visited class tab in localStorage
  const savedTab = localStorage.getItem('lastVisitedClass');
  if (savedTab) {
    const tabButton = document.querySelector(`[onclick="showClass('${savedTab}')"]`);
    if (tabButton) {
      tabButton.click();
    }
  }
  
  // Save current tab when switching
  const tabButtons = document.querySelectorAll('.tab-button');
  tabButtons.forEach(button => {
    button.addEventListener('click', function() {
      const classMatch = this.getAttribute('onclick').match(/showClass\('(\w+)'\)/);
      if (classMatch) {
        localStorage.setItem('lastVisitedClass', classMatch[1]);
      }
    });
  });
});

// Utility function to format resource names for file paths
function formatResourceName(name) {
  return name.toLowerCase()
             .replace(/\s+/g, '_')
             .replace(/[^a-z0-9_]/g, '');
}

// Function to track most popular resources
function trackResourceUsage(resourceName) {
  let usage = JSON.parse(localStorage.getItem('resourceUsage') || '{}');
  usage[resourceName] = (usage[resourceName] || 0) + 1;
  localStorage.setItem('resourceUsage', JSON.stringify(usage));
}
