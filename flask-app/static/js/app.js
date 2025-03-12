// Helper functions for the application

/**
 * Format a date string in a user-friendly format
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString(undefined, options);
}

/**
 * Make text content safe for display in HTML
 * @param {string} text - The raw text
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show a toast notification
 * @param {string} message - The notification message
 * @param {string} type - The type of notification (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    // Map type to Bootstrap alert class
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`;
    alert.setAttribute('role', 'alert');
    alert.style.zIndex = 1050;
    
    // Set content
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to document
    document.body.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

/**
 * Validate file input for size and type
 * @param {HTMLInputElement} fileInput - The file input element
 * @param {Array} allowedTypes - Array of allowed file extensions
 * @param {number} maxSize - Maximum file size in bytes
 * @returns {boolean} - Whether the file is valid
 */
function validateFileInput(fileInput, allowedTypes, maxSize = 100 * 1024 * 1024) {
    if (!fileInput.files || fileInput.files.length === 0) {
        showNotification('Please select a file', 'warning');
        return false;
    }
    
    const file = fileInput.files[0];
    
    // Check file type
    const fileExtension = file.name.split('.').pop().toLowerCase();
    if (!allowedTypes.includes(fileExtension)) {
        showNotification(`Invalid file type. Allowed types: ${allowedTypes.join(', ')}`, 'error');
        return false;
    }
    
    // Check file size
    if (file.size > maxSize) {
        const maxSizeMB = maxSize / (1024 * 1024);
        showNotification(`File is too large. Maximum size is ${maxSizeMB}MB.`, 'error');
        return false;
    }
    
    return true;
}

// Add event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add file input validation for upload forms
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const allowedTypes = this.accept ? 
                this.accept.split(',').map(type => type.trim().replace('.', '')) : 
                ['mp3', 'wav', 'm4a', 'ogg'];
            
            validateFileInput(this, allowedTypes);
        });
    });
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
});
