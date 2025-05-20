export function showAlert(message, type = 'info') {
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