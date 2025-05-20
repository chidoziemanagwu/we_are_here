// CSRF Token handling
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Show alert messages
function showAlert(message, type = 'info') {
    const alertElement = document.createElement('div');
    alertElement.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    alertElement.textContent = message;

    document.body.appendChild(alertElement);

    // Remove alert after 3 seconds
    setTimeout(() => {
        alertElement.remove();
    }, 3000);
}

// Get directions to a location
// Get directions to a location
function getDirections(lat, lng) {
    // Check if the device is mobile
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    // Create the appropriate maps URL
    let mapsUrl;
    if (isMobile) {
        // Mobile devices - try to use native maps app
        if (navigator.platform.indexOf('iPhone') != -1 || 
            navigator.platform.indexOf('iPad') != -1 || 
            navigator.platform.indexOf('iPod') != -1) {
            mapsUrl = `maps://maps.apple.com/?daddr=${lat},${lng}`;
        } else {
            mapsUrl = `geo:${lat},${lng}?q=${lat},${lng}`;
        }
    } else {
        // Desktop - use Google Maps
        mapsUrl = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    }
    
    // Open in new tab
    window.open(mapsUrl, '_blank');
}

// Make function available globally
window.getDirections = getDirections;



// Update service status
function updateServiceStatus(serviceId, newStatus) {
    fetch(`/service/${serviceId}/status/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `status=${newStatus}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update status display
            const statusElement = document.getElementById('service-status');
            statusElement.textContent = data.data.status_display;
            
            // Update status classes
            statusElement.className = `px-2 py-1 text-sm rounded-full ${
                data.data.status === 'available' ? 'bg-green-100 text-green-800' :
                data.data.status === 'limited' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
            }`;
            
            showAlert('Status updated successfully', 'success');
        } else {
            showAlert('Error updating status: ' + data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error updating status. Please try again.', 'error');
    });
}

// Attach event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Attach event listeners to status update buttons
    document.querySelectorAll('[data-status-update]').forEach(button => {
        button.addEventListener('click', function() {
            const serviceId = this.dataset.serviceId;
            const newStatus = this.dataset.status;
            updateServiceStatus(serviceId, newStatus);
        });
    });
});

// Make functions available globally
window.getDirections = getDirections;
window.updateServiceStatus = updateServiceStatus;
window.showAlert = showAlert;