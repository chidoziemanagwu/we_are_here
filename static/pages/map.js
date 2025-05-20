export function initializeMap(services) {
    // Initialize map
    const map = L.map('map').setView([51.505, -0.09], 13);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Try to get user location
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            map.setView([lat, lng], 13);
            
            // Add a marker for user location
            L.marker([lat, lng])
                .addTo(map)
                .bindPopup('You are here')
                .openPopup();
        });
    }

    // Add service markers
    services.forEach(service => {
        L.marker([service.latitude, service.longitude])
            .addTo(map)
            .bindPopup(`
                <div class="max-w-sm">
                    <h3 class="font-semibold">${service.name}</h3>
                    <p class="text-sm text-gray-600">${service.short_description}</p>
                    <a href="/service/${service.slug}/" 
                       class="text-blue-600 hover:text-blue-800 text-sm">
                        View Details
                    </a>
                </div>
            `);
    });

    return map;
}

export function initializeFilters() {
    // Handle category filters
    document.querySelectorAll('[data-category-filter]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            const selectedCategories = [...document.querySelectorAll('[data-category-filter]:checked')]
                .map(cb => cb.value);
            
            if (selectedCategories.length) {
                currentUrl.searchParams.set('category', selectedCategories.join(','));
            } else {
                currentUrl.searchParams.delete('category');
            }
            
            window.location = currentUrl;
        });
    });

    // Handle status filters
    document.querySelectorAll('[data-status-filter]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const currentUrl = new URL(window.location.href);
            const selectedStatuses = [...document.querySelectorAll('[data-status-filter]:checked')]
                .map(cb => cb.value);
            
            if (selectedStatuses.length) {
                currentUrl.searchParams.set('status', selectedStatuses.join(','));
            } else {
                currentUrl.searchParams.delete('status');
            }
            
            window.location = currentUrl;
        });
    });

    // Handle location search
    const searchInput = document.getElementById('location-search');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                // Here you would typically use a geocoding service
                alert('Location search functionality coming soon!');
            }
        });
    }
}