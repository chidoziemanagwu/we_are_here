import { getCsrfToken } from '../utils/csrf.js';
import { showAlert } from '../utils/alerts.js';

// Service detail page functionality
document.addEventListener('DOMContentLoaded', function() {
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

    // Attach event listeners to status update buttons
    document.querySelectorAll('[data-status-update]').forEach(button => {
        button.addEventListener('click', function() {
            const serviceId = this.dataset.serviceId;
            const newStatus = this.dataset.status;
            updateServiceStatus(serviceId, newStatus);
        });
    });
});