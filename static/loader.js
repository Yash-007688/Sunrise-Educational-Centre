// loader.js
document.addEventListener('DOMContentLoaded', function () {
    fetch('/static/modern-navbar-component.html')
        .then(response => response.text())
        .then(data => {
            const navbarContainer = document.getElementById('navbar-container');
            if (navbarContainer) {
                navbarContainer.innerHTML = data;
            }

            // Dynamically load the navbar script to ensure it executes after the HTML is in place
            const script = document.createElement('script');
            script.src = '/static/modern-navbar.js';
            document.head.appendChild(script);
        })
        .catch(error => {
            console.error('Error loading the navbar:', error);
        });
});
