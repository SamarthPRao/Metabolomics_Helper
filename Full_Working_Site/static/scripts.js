document.addEventListener('DOMContentLoaded', function () {
  // Sidebar toggle logic
  const sidebar = document.querySelector('.sidebar');
  const toggleButton = document.getElementById('sidebarToggle');

  toggleButton.addEventListener('click', function (event) {
    event.stopPropagation();
    sidebar.classList.toggle('collapsed');
    sidebar.classList.toggle('hide-text');
  });

  // Card hover background blur logic
  const background = document.getElementById('background-blur');
  const cards = document.querySelectorAll('.card');

  cards.forEach(card => {
    card.addEventListener('mouseenter', () => {
      background.classList.add('blurred');
    });
    card.addEventListener('mouseleave', () => {
      background.classList.remove('blurred');
    });
  });
});