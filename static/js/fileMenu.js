document.addEventListener('DOMContentLoaded', function () {
    // Get all toggle buttons
    const toggleButtons = document.querySelectorAll('.toggle-menu-btn');

    toggleButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            // Find the corresponding file menu (siblings)
            const fileMenu = this.closest('.file-options').querySelector('.file-menu');
            
            // If the file menu exists, toggle its display
            if (fileMenu) {
                // Prevent event propagation to avoid closing the menu when clicking the toggle button itself
                event.stopPropagation();

                // Toggle the show class on the file menu
                if (fileMenu.classList.contains('show')) {
                    fileMenu.classList.remove('show'); // Hide the menu with animation
                } else {
                    fileMenu.classList.add('show'); // Show the menu with animation
                }
            }
        });
    });

    // Close the menu if clicking anywhere outside
    document.addEventListener('click', function(event) {
        // Get all open file menus
        const openMenus = document.querySelectorAll('.file-menu.show');

        openMenus.forEach(function(menu) {
            // If the click is outside the menu and not on the toggle button
            if (!menu.contains(event.target) && !menu.previousElementSibling.contains(event.target)) {
                menu.classList.remove('show'); // Close the menu
            }
        });
    });
});
