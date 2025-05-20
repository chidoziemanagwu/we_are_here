export function initializeFilters() {
    const categoryFilters = document.querySelectorAll('[data-category-filter]');
    const statusFilters = document.querySelectorAll('[data-status-filter]');
    const searchInput = document.getElementById('location-search');

    // Set initial filter states from URL
    const urlParams = new URLSearchParams(window.location.search);
    
    // Set category checkboxes
    const categories = urlParams.get('category')?.split(',') || [];
    categoryFilters.forEach(checkbox => {
        checkbox.checked = categories.includes(checkbox.value);
    });

    // Set status checkboxes
    const statuses = urlParams.get('status')?.split(',') || ['available', 'limited'];
    statusFilters.forEach(checkbox => {
        checkbox.checked = statuses.includes(checkbox.value);
    });

    // Handle filter changes
    function updateFilters() {
        const currentUrl = new URL(window.location.href);
        
        // Update categories
        const selectedCategories = [...categoryFilters]
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        if (selectedCategories.length) {
            currentUrl.searchParams.set('category', selectedCategories.join(','));
        } else {
            currentUrl.searchParams.delete('category');
        }

        // Update statuses
        const selectedStatuses = [...statusFilters]
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        if (selectedStatuses.length) {
            currentUrl.searchParams.set('status', selectedStatuses.join(','));
        } else {
            currentUrl.searchParams.delete('status');
        }

        // Navigate to filtered URL
        window.location = currentUrl;
    }

    // Attach event listeners
    categoryFilters.forEach(checkbox => {
        checkbox.addEventListener('change', updateFilters);
    });

    statusFilters.forEach(checkbox => {
        checkbox.addEventListener('change', updateFilters);
    });

    // Handle search
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('q', this.value);
                window.location = currentUrl;
            }
        });
    }
}