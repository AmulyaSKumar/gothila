// Legal Document Checker - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File size formatter
    window.formatFileSize = function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    // Progress bar animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 100);
    });

    // Copy to clipboard functionality
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy to clipboard', 'error');
        });
    };

    // Toast notification system
    window.showToast = function(message, type = 'info') {
        const toastContainer = getOrCreateToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastHTML = `
            <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header">
                    <i class="fas fa-${getToastIcon(type)} me-2 text-${type}"></i>
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    };

    function getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1060';
            document.body.appendChild(container);
        }
        return container;
    }

    function getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || icons.info;
    }

    // Document processing status checker
    window.checkProcessingStatus = function(documentId) {
        fetch(`/api/processing-status/${documentId}`)
            .then(response => response.json())
            .then(data => {
                updateProcessingStatus(documentId, data);
                if (!data.processed && data.status !== 'failed') {
                    setTimeout(() => checkProcessingStatus(documentId), 5000);
                }
            })
            .catch(error => {
                console.error('Error checking status:', error);
            });
    };

    function updateProcessingStatus(documentId, data) {
        const statusElements = document.querySelectorAll(`[data-document-id="${documentId}"]`);
        statusElements.forEach(element => {
            if (element.classList.contains('status-badge')) {
                if (data.processed) {
                    element.className = 'badge bg-success status-badge';
                    element.innerHTML = '<i class="fas fa-check-circle me-1"></i>Completed';
                } else if (data.status === 'failed') {
                    element.className = 'badge bg-danger status-badge';
                    element.innerHTML = '<i class="fas fa-times-circle me-1"></i>Failed';
                } else {
                    element.className = 'badge bg-warning status-badge';
                    element.innerHTML = `<i class="fas fa-spinner fa-spin me-1"></i>${data.status}`;
                }
            }
            
            if (element.classList.contains('compliance-score')) {
                if (data.compliance_score) {
                    element.textContent = `${data.compliance_score.toFixed(1)}%`;
                }
            }
        });
    }

    // Initialize any processing status checkers on page load
    const processingElements = document.querySelectorAll('[data-processing="true"]');
    processingElements.forEach(element => {
        const documentId = element.dataset.documentId;
        if (documentId) {
            checkProcessingStatus(documentId);
        }
    });

    // Search functionality for tables
    window.initTableSearch = function(tableId, searchInputId) {
        const table = document.getElementById(tableId);
        const searchInput = document.getElementById(searchInputId);
        
        if (!table || !searchInput) return;
        
        searchInput.addEventListener('keyup', function() {
            const filter = this.value.toLowerCase();
            const rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
            
            Array.from(rows).forEach(row => {
                const cells = row.getElementsByTagName('td');
                let found = false;
                
                Array.from(cells).forEach(cell => {
                    if (cell.textContent.toLowerCase().includes(filter)) {
                        found = true;
                    }
                });
                
                row.style.display = found ? '' : 'none';
            });
        });
    };

    // Debounce function for performance
    window.debounce = function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    };

    // Theme preference handling
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Handle theme changes
    prefersDarkScheme.addEventListener('change', (e) => {
        // Could implement dark mode theme switching here
        console.log('Theme preference changed:', e.matches ? 'dark' : 'light');
    });
});

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Could send error reports to monitoring service
});

// Service worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Service worker could be registered here for offline functionality
        console.log('Service Worker support detected');
    });
}
