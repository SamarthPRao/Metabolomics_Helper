document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.querySelector('.sidebar');
  const toggleButton = document.getElementById('sidebarToggle');

  // Toggle the collapsed class (existing functionality)
  toggleButton.addEventListener('click', function(event) {
    event.stopPropagation(); // Prevent the sidebar click event from firing too
    sidebar.classList.toggle('collapsed');
    sidebar.classList.toggle('hide-text');
  });

});