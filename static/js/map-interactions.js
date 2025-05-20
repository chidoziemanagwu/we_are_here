// Global variable for map access in filter functions
let globalMap;
let globalMarkers = {};

// Filter markers based on selected categories - fixed to use global variables
function filterMarkersByCategory(selectedCategories) {
    console.log("Filtering markers by categories:", selectedCategories);
    
    // If no categories selected, hide all markers
    if (!selectedCategories || selectedCategories.length === 0) {
        console.log("No categories selected, hiding all markers");
        Object.values(globalMarkers).forEach(marker => {
            marker.setMap(null);
        });
        return;
    }
    
    // Count for logging
    let shownCount = 0;
    let hiddenCount = 0;
    
    // Show/hide markers based on category
    Object.values(globalMarkers).forEach(marker => {
        if (!marker || !marker.service) {
            console.warn("Marker or marker.service is undefined");
            return;
        }
        
        const category = marker.service.category;
        
        if (selectedCategories.includes(category)) {
            // Show marker
            marker.setMap(globalMap);
            shownCount++;
        } else {
            // Hide marker
            marker.setMap(null);
            hiddenCount++;
        }
    });
    
    console.log(`Filter applied: ${shownCount} markers shown, ${hiddenCount} markers hidden`);
}

// Make the function available globally
window.filterServiceMarkers = filterMarkersByCategory;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize map
    const mapElement = document.getElementById('map');
    if (!mapElement) return;
    
    console.log("Map initialization started");

    // Define category colors for markers - EXACTLY matching the legend
    const categoryColors = {
        "Shelters": "#E31A1C",
        "Food Services": "#31B404", 
        "Medical Support": "#FF69B4",
        "Mental Health": "#9370DB",
        "Clothing Support": "#FF8C00",
        "Shower Facilities": "#1E90FF",
        "Employment Support": "#FFD700",
        "Legal Support": "#ADD8E6"
    };
    
    // Category to icon mapping - using the exact same colors as the legend
    const categoryIcons = {
        "Shelters": "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
        "Food Services": "https://maps.google.com/mapfiles/ms/icons/green-dot.png",
        "Medical Support": "https://maps.google.com/mapfiles/ms/icons/pink-dot.png",
        "Mental Health": "https://maps.google.com/mapfiles/ms/icons/purple-dot.png",
        "Clothing Support": "https://maps.google.com/mapfiles/ms/icons/orange-dot.png",
        "Shower Facilities": "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        "Employment Support": "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
        "Legal Support": "https://maps.google.com/mapfiles/ms/icons/ltblue-dot.png"
    };
    
    // Initialize Google Map with optimized settings
    const map = new google.maps.Map(mapElement, {
        center: { lat: 51.505, lng: -0.09 },
        zoom: 13,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
        gestureHandling: 'greedy',
        // Reduce map style complexity for faster rendering
        styles: [
            {
                featureType: "poi",
                elementType: "labels",
                stylers: [{ visibility: "off" }]
            },
            {
                featureType: "transit",
                elementType: "labels",
                stylers: [{ visibility: "off" }]
            }
        ]
    });
    
    // Set global map for filter functions
    globalMap = map;
    
    // Use a single infoWindow instance for all markers (better performance)
    const infoWindow = new google.maps.InfoWindow();
    
    // Reference for user marker
    let userMarker = null;
    
    // Use object for markers instead of array for faster operations
    const markers = {};
    // Set global markers for filter functions
    globalMarkers = markers;
    
    // Add user location marker
    function addUserMarker(lat, lng) {
        // Remove existing user marker
        if (userMarker) {
            userMarker.setMap(null);
        }
        
        // Create new user marker with house icon
        userMarker = new google.maps.Marker({
            position: { lat, lng },
            map: map,
            title: 'Your Location',
            icon: {
                url: 'https://maps.google.com/mapfiles/ms/icons/homegardenbusiness.png',
                scaledSize: new google.maps.Size(40, 40)
            },
            zIndex: 1000,
            optimized: true,
            label: null // Explicitly set to null to prevent "Mark" text
        });
        
        // Add info window
        const userInfoContent = '<div class="service-popup"><div class="popup-header"><h3 class="text-lg font-bold">Your Location</h3></div></div>';
        
        userMarker.addListener('click', () => {
            infoWindow.setContent(userInfoContent);
            infoWindow.open(map, userMarker);
        });
        
        return userMarker;
    }
    
    // Pre-compile popup content creation for better performance
    function createPopupContent(service) {
        return `
            <div class="service-popup p-0 max-w-sm">
                <div class="bg-gradient-to-r from-blue-600 to-blue-800 p-4 rounded-t-lg">
                    <div class="flex justify-between items-start">
                        <h3 class="text-lg font-bold text-white">${service.name}</h3>
                        ${service.status ? `
                            <span class="inline-block px-2 py-1 text-xs font-medium rounded-full ms-2 ${getStatusBadgeClass(service.status)}">
                                ${formatStatus(service.status)}
                            </span>
                        ` : ''}
                    </div>
                    ${service.category ? `
                        <div class="mt-2">
                            <span class="inline-block px-2 py-1 text-xs font-medium rounded-full bg-blue-200 text-blue-800">
                                ${service.category}
                            </span>
                        </div>
                    ` : ''}
                </div>
                
                <div class="bg-white p-4 rounded-b-lg shadow-inner">
                    ${service.shortDescription ? `
                        <p class="mb-4 text-sm text-gray-700">
                            ${service.shortDescription}
                        </p>
                    ` : ''}
                    
                    <div class="space-y-2 mb-4">
                        ${service.address && service.address !== 'Address not available' ? `
                            <div class="flex items-start">
                                <i class="fas fa-location-dot text-red-500 mt-1 mr-2"></i>
                                <span class="text-sm text-gray-700">${service.address}</span>
                            </div>
                        ` : ''}
                        
                        ${service.openingHours && service.openingHours !== 'Hours not specified' && service.openingHours !== 'Hours not available' ? `
                            <div class="flex items-start">
                                <i class="fas fa-clock text-blue-500 mt-1 mr-2"></i>
                                <span class="text-sm text-gray-700">${service.openingHours}</span>
                            </div>
                        ` : ''}
                        
                        ${service.phone && service.phone !== 'Phone not available' ? `
                            <div class="flex items-start">
                                <i class="fas fa-phone text-green-500 mt-1 mr-2"></i>
                                <a href="tel:${service.phone}" class="text-sm text-blue-600 hover:text-blue-800">${service.phone}</a>
                            </div>
                        ` : ''}
                        
                        ${service.website && service.website !== '#' ? `
                            <div class="flex items-start">
                                <i class="fas fa-globe text-purple-500 mt-1 mr-2"></i>
                                <a href="${service.website}" target="_blank" class="text-sm text-blue-600 hover:text-blue-800">Visit Website</a>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="flex gap-2">
                        <a href="https://www.google.com/maps/dir/?api=1&destination=${service.latitude},${service.longitude}" 
                        target="_blank" 
                        class="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg text-center">
                            <i class="fas fa-directions mr-2"></i> Directions
                        </a>
                        
                        ${!service.isExternal && service.slug ? `
                            <a href="/service/${service.slug}/" 
                            class="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg text-center">
                                <i class="fas fa-info-circle mr-2"></i> Details
                            </a>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    

    // Helper function to get status badge class
    function getStatusBadgeClass(status) {
        switch(status) {
            case 'available':
                return 'bg-green-100 text-green-800';
            case 'limited':
                return 'bg-yellow-100 text-yellow-800';
            case 'unavailable':
                return 'bg-red-100 text-red-800';
            default:
                return 'bg-gray-100 text-gray-800';
        }
    }

    function formatStatus(status) {
        switch(status) {
            case 'available':
                return 'Available';
            case 'limited':
                return 'Limited';
            case 'unavailable':
                return 'Unavailable';
            default:
                return 'Unknown';
        }
    }

    // Lazy load markers - only create markers for visible viewport
    function addServiceMarkers(bounds = null) {
        // Clear existing markers
        Object.values(markers).forEach(marker => marker.setMap(null));
        Object.keys(markers).forEach(key => delete markers[key]);
        
        // Check if we have service data
        if (!window.allServiceData || window.allServiceData.length === 0) {
            console.log("No service data found");
            return;
        }
        
        console.log(`Processing ${window.allServiceData.length} services`);
        
        // Get current map bounds if not provided
        if (!bounds) {
            bounds = map.getBounds();
            // If bounds not ready yet, use a larger area around center
            if (!bounds) {
                const center = map.getCenter();
                bounds = {
                    contains: () => true // Show all markers initially
                };
            }
        }
        
        // Batch marker creation for better performance
        const batch = [];
        
        window.allServiceData.forEach(service => {
            // Skip services with invalid coordinates
            if (!service.latitude || !service.longitude) {
                return;
            }
            
            // Parse coordinates as floats
            const lat = parseFloat(service.latitude);
            const lng = parseFloat(service.longitude);
            
            if (isNaN(lat) || isNaN(lng)) {
                return;
            }
            
            // Skip if outside current viewport (with buffer)
            const position = new google.maps.LatLng(lat, lng);
            if (bounds.contains && !bounds.contains(position)) {
                return;
            }
            
            // Get category
            const categoryName = service.category || "Shelters"; // Default to Shelters
            
            // Get icon based on category
            let iconUrl = categoryIcons[categoryName] || "https://maps.google.com/mapfiles/ms/icons/red-dot.png"; // Default
            
            // Update the icon definition in the batch.push section:
            batch.push({
                id: service.id,
                position: position,
                title: service.name,
                icon: {
                    url: iconUrl,
                    scaledSize: new google.maps.Size(32, 32),
                    labelOrigin: new google.maps.Point(16, -10), // Move label position away from marker
                },
                service: service
            });
        });
        
        // Create markers in batches for better performance
        requestAnimationFrame(() => {
            batch.forEach(item => {
                const marker = new google.maps.Marker({
                    position: item.position,
                    map: map,
                    title: item.title,
                    icon: {
                        url: item.icon.url,
                        scaledSize: new google.maps.Size(32, 32),
                        // The following line is crucial to remove the "Mark" text
                        labelOrigin: new google.maps.Point(0, 0)
                    },
                    optimized: true,
                    // Set label to an empty object instead of null
                    label: {
                        text: "",
                        color: "transparent"
                    }
                });
                
                // Use event delegation for better performance
                marker.addListener('click', () => {
                    const popupContent = createPopupContent(item.service);
                    infoWindow.setContent(popupContent);
                    infoWindow.open(map, marker);
                });
                
                marker.service = item.service;
                markers[item.id] = marker;
                
                // Update global markers reference
                globalMarkers = markers;
            });
            
            // Apply any active filters after adding markers
            applyActiveFilters();
        });
    }
    
    // Function to apply active filters from URL or checkboxes
    function applyActiveFilters() {
        const categoryCheckboxes = document.querySelectorAll('.category-checkbox');
        if (categoryCheckboxes.length > 0) {
            const selectedCategories = Array.from(categoryCheckboxes)
                .filter(checkbox => checkbox.checked)
                .map(checkbox => checkbox.value);
                
            if (selectedCategories.length > 0) {
                console.log("Applying active filters:", selectedCategories);
                filterMarkersByCategory(selectedCategories);
            }
        }
    }
    
    // Optimized service fetching with caching
    const serviceCache = {};
    
    function fetchServicesForLocation(lat, lng) {
        // Check cache first (rounded to 4 decimal places for better cache hits)
        const cacheKey = `${lat.toFixed(4)},${lng.toFixed(4)}`;
        if (serviceCache[cacheKey]) {
            console.log("Using cached services data");
            window.allServiceData = serviceCache[cacheKey];
            addServiceMarkers();
            return Promise.resolve();
        }
        
        // Create URL with the new location
        const apiUrl = new URL(window.location.origin + window.location.pathname);
        apiUrl.searchParams.set('lat', lat);
        apiUrl.searchParams.set('lng', lng);
        apiUrl.searchParams.set('ajax', 'true'); // Flag to indicate this is an AJAX request
        
        // Preserve existing filters
        preserveFiltersInUrl(apiUrl);
        
        // Show loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'map-loading-indicator';
        loadingIndicator.innerHTML = `
            <i class="fas fa-spinner fa-spin fa-2x"></i>
            <span>Loading services...</span>
        `;
        mapElement.appendChild(loadingIndicator);
        
        // Use fetch with timeout for better responsiveness
        const fetchPromise = fetch(apiUrl);
        const timeoutPromise = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Request timed out')), 8000)
        );
        
        return Promise.race([fetchPromise, timeoutPromise])
            .then(response => response.json())
            .then(data => {
                // Cache the results
                window.allServiceData = data.services || [];
                serviceCache[cacheKey] = window.allServiceData;
                console.log(`Received ${window.allServiceData.length} services for the new location`);
                
                // Clear existing markers
                Object.values(markers).forEach(marker => marker.setMap(null));
                Object.keys(markers).forEach(key => delete markers[key]);
                
                // Add markers
                addServiceMarkers();
                
                // Remove loading indicator
                if (mapElement.contains(loadingIndicator)) {
                    mapElement.removeChild(loadingIndicator);
                }
            })
            .catch(error => {
                console.error('Error fetching services:', error);
                
                // If ajax fetch fails, do a full page reload instead
                const fullUrl = new URL(window.location.href);
                fullUrl.searchParams.set('lat', lat);
                fullUrl.searchParams.set('lng', lng);
                preserveFiltersInUrl(fullUrl);
                
                // Remove loading indicator
                if (mapElement.contains(loadingIndicator)) {
                    mapElement.removeChild(loadingIndicator);
                }
                
                // Redirect to the full URL
                window.location = fullUrl;
            });
    }
    
    // Helper function to preserve filters in URL
    function preserveFiltersInUrl(url) {
        // Categories from category-checkbox class
        const selectedCategories = [...document.querySelectorAll('.category-checkbox:checked')]
            .map(cb => cb.value);
        if (selectedCategories.length) {
            url.searchParams.set('categories', selectedCategories.join(','));
        }
        
        // Also check data-category-filter for backward compatibility
        const dataSelectedCategories = [...document.querySelectorAll('[data-category-filter]:checked')]
            .map(cb => cb.value);
        if (dataSelectedCategories.length) {
            url.searchParams.set('category', dataSelectedCategories.join(','));
        }
        
        // Statuses
        const selectedStatuses = [...document.querySelectorAll('[data-status-filter]:checked')]
            .map(cb => cb.value);
        if (selectedStatuses.length) {
            url.searchParams.set('status', selectedStatuses.join(','));
        }
        
        // Demographics
        const selectedDemographics = [...document.querySelectorAll('[data-demographic-filter]:checked')]
            .map(cb => cb.value);
        if (selectedDemographics.length) {
            url.searchParams.set('demographic', selectedDemographics.join(','));
        }
    }
    
    // Optimized map initialization
    function initMap() {
        console.log("Initializing map");
        
        // We'll use the home button from the HTML template instead of creating a new one
        // This prevents duplicate home buttons
        
        // Add service markers
        addServiceMarkers();
        
        // Try to get user location
        const urlParams = new URLSearchParams(window.location.search);
        const urlLat = parseFloat(urlParams.get('lat'));
        const urlLng = parseFloat(urlParams.get('lng'));
        
        if (!isNaN(urlLat) && !isNaN(urlLng)) {
            // Use coordinates from URL
            map.setCenter({ lat: urlLat, lng: urlLng });
            map.setZoom(14);
            addUserMarker(urlLat, urlLng);
        } else if (navigator.geolocation) {
            // Try to get current location
            const options = {
                enableHighAccuracy: false, // Lower accuracy for faster response
                timeout: 5000,
                maximumAge: 60000 // Cache position for 1 minute
            };
            
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                // Update URL
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('lat', lat);
                currentUrl.searchParams.set('lng', lng);
                window.history.replaceState({}, '', currentUrl);
                
                // Center map
                map.setCenter({ lat, lng });
                map.setZoom(14);
                
                // Add user marker
                addUserMarker(lat, lng);
                
                // Fetch services for this location
                fetchServicesForLocation(lat, lng);
            }, function(error) {
                console.error("Geolocation error:", error);
                // Default to fallback location
                map.setCenter({ lat: 51.505, lng: -0.09 });
                map.setZoom(12);
            },
            options);
        }
        
        // Add viewport change listener to load markers as user pans/zooms
        map.addListener('idle', function() {
            // Only reload markers if map has moved significantly
            const bounds = map.getBounds();
            if (bounds) {
                addServiceMarkers(bounds);
            }
        });
    }
    
    // Initialize location search
    const searchInput = document.getElementById('location-search');
    if (searchInput) {
        // Initialize Google Places Autocomplete
        if (window.google && window.google.maps && window.google.maps.places) {
            const autocomplete = new google.maps.places.Autocomplete(searchInput);
            
            // Handle Enter key press in search input - THIS IS THE FIX
            searchInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault(); // Prevent default form submission
                    
                    // Get the input value
                    const address = searchInput.value;
                    if (!address) return;
                    
                    // Show loading state
                    searchInput.disabled = true;
                    searchInput.classList.add('bg-gray-100');
                    
                    // Use Geocoding API to convert address to coordinates
                    const geocoder = new google.maps.Geocoder();
                    geocoder.geocode({ address: address }, function(results, status) {
                        if (status === 'OK' && results[0]) {
                            const lat = results[0].geometry.location.lat();
                            const lng = results[0].geometry.location.lng();
                            
                            // Update map
                            map.setCenter(results[0].geometry.location);
                            map.setZoom(14);
                            
                            // Add user marker
                            addUserMarker(lat, lng);
                            
                            // Fetch services for this location
                            fetchServicesForLocation(lat, lng);
                            
                            // Update URL without reload
                            const currentUrl = new URL(window.location.href);
                            currentUrl.searchParams.set('lat', lat);
                            currentUrl.searchParams.set('lng', lng);
                            preserveFiltersInUrl(currentUrl);
                            window.history.replaceState({}, '', currentUrl);
                            
                            // Reset input state
                            searchInput.disabled = false;
                            searchInput.classList.remove('bg-gray-100');
                        } else {
                            // Show error
                            alert("Location not found. Please try a different search.");
                            searchInput.disabled = false;
                            searchInput.classList.remove('bg-gray-100');
                        }
                    });
                }
            });
            
            // In the autocomplete.addListener('place_changed', function() {...}) section:
            autocomplete.addListener('place_changed', function() {
                const place = autocomplete.getPlace();
                
                if (!place.geometry) {
                    alert("No location found for: " + place.name);
                    return;
                }
                
                // Get coordinates
                const lat = place.geometry.location.lat();
                const lng = place.geometry.location.lng();
                
                // Update map
                map.setCenter(place.geometry.location);
                map.setZoom(14);
                
                // Update URL
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.set('lat', lat);
                currentUrl.searchParams.set('lng', lng);
                
                // Add user marker
                addUserMarker(lat, lng);
                
                // Preserve filters
                preserveFiltersInUrl(currentUrl);
                
                // Update URL without reload
                window.history.replaceState({}, '', currentUrl);
                
                // Fetch services for this location - THIS IS THE KEY PART
                fetchServicesForLocation(lat, lng);
            });
        } else {
            console.error("Google Places API not available");
            searchInput.placeholder = "Search not available";
            searchInput.disabled = true;
        }
    }
    
    // Handle category filters with AJAX instead of page reload
    document.querySelectorAll('[data-category-filter]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const selectedCategories = [...document.querySelectorAll('[data-category-filter]:checked')]
                .map(cb => cb.value);
            
            // Update URL without reloading
            const currentUrl = new URL(window.location.href);
            if (selectedCategories.length) {
                currentUrl.searchParams.set('category', selectedCategories.join(','));
            } else {
                currentUrl.searchParams.delete('category');
            }
            window.history.replaceState({}, '', currentUrl);
            
            // Filter markers
            filterMarkersByCategory(selectedCategories);
        });
    });
    
    // Handle category checkboxes with class 'category-checkbox'
    document.querySelectorAll('.category-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const selectedCategories = [...document.querySelectorAll('.category-checkbox:checked')]
                .map(cb => cb.value);
            
            // Update URL without reloading
            const currentUrl = new URL(window.location.href);
            if (selectedCategories.length) {
                currentUrl.searchParams.set('categories', selectedCategories.join(','));
            } else {
                currentUrl.searchParams.delete('categories');
            }
            window.history.replaceState({}, '', currentUrl);
            
            // Filter markers
            filterMarkersByCategory(selectedCategories);
        });
    });

    // Handle status filters with AJAX instead of page reload
    document.querySelectorAll('[data-status-filter]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const selectedStatuses = [...document.querySelectorAll('[data-status-filter]:checked')]
                .map(cb => cb.value);
            
            // Update URL without reloading
            const currentUrl = new URL(window.location.href);
            if (selectedStatuses.length) {
                currentUrl.searchParams.set('status', selectedStatuses.join(','));
            } else {
                currentUrl.searchParams.delete('status');
            }
            window.history.replaceState({}, '', currentUrl);
            
            // You can add status filtering logic here if needed
        });
    });
    
    // Handle demographic filters with AJAX instead of page reload
    document.querySelectorAll('[data-demographic-filter]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const selectedDemographics = [...document.querySelectorAll('[data-demographic-filter]:checked')]
                .map(cb => cb.value);
            
            // Update URL without reloading
            const currentUrl = new URL(window.location.href);
            if (selectedDemographics.length) {
                currentUrl.searchParams.set('demographic', selectedDemographics.join(','));
            } else {
                currentUrl.searchParams.delete('demographic');
            }
            window.history.replaceState({}, '', currentUrl);
            
            // You can add demographic filtering logic here if needed
        });
    });
    
    // Handle floating action button
    const floatingBtn = document.querySelector('.floating-action-button');
    if (floatingBtn) {
        floatingBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                floatingBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                // Use high accuracy only on mobile devices
                const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
                
                const options = {
                    enableHighAccuracy: isMobile,
                    timeout: 5000,
                    maximumAge: 60000 // Cache position for 1 minute
                };
                
                navigator.geolocation.getCurrentPosition(position => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    // Try AJAX first
                    try {
                        // Update map
                        map.setCenter({ lat, lng });
                        map.setZoom(14);
                        
                        // Add user marker
                        addUserMarker(lat, lng);
                        
                        // Fetch new services
                        fetchServicesForLocation(lat, lng);
                        
                        // Success indicator
                        floatingBtn.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => {
                            floatingBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                        }, 1000);
                    } catch (error) {
                        console.error("Error updating map:", error);
                        
                        // Fallback: full page reload
                        const currentUrl = new URL(window.location.href);
                        currentUrl.searchParams.set('lat', lat);
                        currentUrl.searchParams.set('lng', lng);
                        
                        // Preserve filters
                        preserveFiltersInUrl(currentUrl);
                        
                        floatingBtn.innerHTML = '<i class="fas fa-check"></i>';
                        setTimeout(() => {
                            window.location = currentUrl;
                        }, 500);
                    }
                }, 
                error => {
                    floatingBtn.innerHTML = '<i class="fas fa-times"></i>';
                    setTimeout(() => {
                        floatingBtn.innerHTML = '<i class="fas fa-crosshairs"></i>';
                    }, 1000);
                    alert("Could not get your location. Please check your permissions.");
                },
                options);
            }
        });
    }
    
    // Initialize map with a slight delay to allow DOM to fully render
    if (window.google && window.google.maps) {
        setTimeout(initMap, 10);
    } else {
        // If Google Maps API isn't loaded yet, wait for it
        window.initMap = initMap;
    }
    
    // Connect the existing home button in the HTML to our functionality
    const homeBtn = document.querySelector('.home-marker-btn');
    if (homeBtn) {
        homeBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                homeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                const options = {
                    enableHighAccuracy: false,
                    timeout: 5000,
                    maximumAge: 60000
                };
                
                navigator.geolocation.getCurrentPosition(position => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    
                    // Update map
                    map.setCenter({ lat, lng });
                    map.setZoom(14);
                    
                    // Add user marker
                    addUserMarker(lat, lng);
                    
                    // Update URL
                    const currentUrl = new URL(window.location.href);
                    currentUrl.searchParams.set('lat', lat);
                    currentUrl.searchParams.set('lng', lng);
                    
                    // Preserve filters
                    preserveFiltersInUrl(currentUrl);
                    
                    // Fetch services for this location
                    fetchServicesForLocation(lat, lng);
                    
                    // Update URL without reload
                    window.history.replaceState({}, '', currentUrl);
                    
                    // Success indicator
                    homeBtn.innerHTML = '<i class="fas fa-check"></i>';
                    setTimeout(() => {
                        homeBtn.innerHTML = '<i class="fas fa-home"></i>';
                    }, 1000);
                }, 
                error => {
                    homeBtn.innerHTML = '<i class="fas fa-times"></i>';
                    setTimeout(() => {
                        homeBtn.innerHTML = '<i class="fas fa-home"></i>';
                    }, 1000);
                    alert("Could not get your location. Please check your permissions.");
                },
                options);
            }
        });
    }
    
    // Handle category filter checkboxes
    const categoryCheckboxes = document.querySelectorAll('.category-checkbox');
    const selectAllBtn = document.getElementById('select-all-btn');
    const clearAllBtn = document.getElementById('clear-all-btn');
    
    if (categoryCheckboxes.length > 0) {
        console.log(`Found ${categoryCheckboxes.length} category checkboxes`);
        
        // Select all button
        if (selectAllBtn) {
            selectAllBtn.addEventListener('click', () => {
                console.log("Select All button clicked");
                categoryCheckboxes.forEach(checkbox => {
                    checkbox.checked = true;
                });
                
                // Get selected categories
                const selectedCategories = Array.from(categoryCheckboxes)
                    .map(checkbox => checkbox.value);
                
                // Update URL
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.delete('categories');
                window.history.replaceState({}, '', currentUrl);
                
                // Apply filtering
                filterMarkersByCategory(selectedCategories);
            });
        }
        
        // Clear all button
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => {
                console.log("Clear All button clicked");
                categoryCheckboxes.forEach(checkbox => {
                    checkbox.checked = false;
                });
                
                // Update URL
                const currentUrl = new URL(window.location.href);
                currentUrl.searchParams.delete('categories');
                window.history.replaceState({}, '', currentUrl);
                
                // Apply filtering (empty array will hide all markers)
                filterMarkersByCategory([]);
            });
        }
        
        // Initialize from URL parameters if present
        const urlParams = new URLSearchParams(window.location.search);
        const categoriesParam = urlParams.get('categories');
        
        if (categoriesParam) {
            const urlCategories = categoriesParam.split(',');
            console.log("Initializing from URL with categories:", urlCategories);
            
            // Uncheck all first
            categoryCheckboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Check only those in URL
            categoryCheckboxes.forEach(checkbox => {
                if (urlCategories.includes(checkbox.value)) {
                    checkbox.checked = true;
                    console.log(`Setting ${checkbox.value} to checked from URL parameter`);
                }
            });
            
            // Apply filtering with a delay to ensure map is loaded
            setTimeout(() => {
                filterMarkersByCategory(urlCategories);
            }, 1000);
        }
    }
});

// Fix the message listener to use Google Maps instead of Leaflet
window.addEventListener('message', function(event) {
    // Check if the message is to center the map on a service
    if (event.data.type === 'centerMapOnService') {
        const serviceId = event.data.serviceId;
        const serviceName = event.data.serviceName;
        const serviceAddress = event.data.serviceAddress;
        
        // If we have coordinates for this service in our markers, center on it
        let found = false;
        
        // Search through all markers
        if (globalMarkers && Object.keys(globalMarkers).length > 0) {
            for (const id in globalMarkers) {
                if (id === serviceId.toString()) {
                    const marker = globalMarkers[id];
                    globalMap.setCenter(marker.getPosition());
                    globalMap.setZoom(16);
                    google.maps.event.trigger(marker, 'click');
                    found = true;
                    break;
                }
            }
        }
        
        // If not found, try to geocode the address
        if (!found && serviceAddress && window.google && window.google.maps && window.google.maps.Geocoder) {
            const geocoder = new google.maps.Geocoder();
            geocoder.geocode({ address: serviceAddress }, function(results, status) {
                if (status === 'OK' && results[0]) {
                    const position = results[0].geometry.location;
                    
                    // Create a temporary marker
                    const tempMarker = new google.maps.Marker({
                        position: position,
                        map: globalMap,
                        title: serviceName
                    });
                    
                    // Create info window
                    const infoWindow = new google.maps.InfoWindow({
                        content: `<b>${serviceName}</b><br>${serviceAddress}`
                    });
                    infoWindow.open(globalMap, tempMarker);
                    
                    // Center the map
                    globalMap.setCenter(position);
                    globalMap.setZoom(16);
                    
                    // Remove marker after a while
                    setTimeout(() => {
                        tempMarker.setMap(null);
                    }, 10000);
                }
            });
        }
    }
});