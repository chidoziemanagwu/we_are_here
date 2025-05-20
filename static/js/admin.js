document.addEventListener('DOMContentLoaded', function() {
    // Mobile sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.admin-sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('hidden');
            sidebar.classList.toggle('md:block');
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('opacity-0');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Initialize any tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        // Add tooltip functionality if needed
    });
});