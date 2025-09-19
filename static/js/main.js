// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle form submissions with AJAX
    document.querySelectorAll('form[data-ajax="true"]').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            
            // Show loading state
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            
            fetch(form.action, {
                method: form.method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show success message
                    showAlert('success', data.message || 'Operation completed successfully.');
                    
                    // Handle redirect if specified
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                    }
                } else {
                    // Show error message
                    showAlert('danger', data.message || 'An error occurred. Please try again.');
                }
            })
            .catch(error => {
                // Show error message
                showAlert('danger', 'An error occurred. Please try again.');
                console.error('Error:', error);
            })
            .finally(() => {
                // Reset button state
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            });
        });
    });

    // Handle image preview
    document.querySelectorAll('input[type="file"][accept*="image"]').forEach(function(input) {
        input.addEventListener('change', function(e) {
            const preview = document.querySelector(this.dataset.preview);
            if (preview && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // Handle quantity input
    document.querySelectorAll('input[type="number"][data-quantity]').forEach(function(input) {
        const min = parseInt(input.min) || 1;
        const max = parseInt(input.max) || 999;
        
        input.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (value < min) this.value = min;
            if (value > max) this.value = max;
        });
    });

    // Handle price formatting
    document.querySelectorAll('[data-price]').forEach(function(element) {
        const price = parseFloat(element.dataset.price);
        if (!isNaN(price)) {
            element.textContent = formatPrice(price);
        }
    });

    // Handle map initialization
    if (typeof L !== 'undefined' && document.getElementById('map')) {
        const map = L.map('map').setView([0, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Add markers if data is available
        if (window.mapData && window.mapData.markers) {
            window.mapData.markers.forEach(function(marker) {
                L.marker([marker.lat, marker.lng])
                    .bindPopup(marker.popup)
                    .addTo(map);
            });
        }
    }
});

// Utility Functions
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        document.body.insertBefore(alertDiv, document.body.firstChild);
    }
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

// Debounce function for performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle function for performance optimization
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Handle infinite scroll
function initInfiniteScroll(container, loadMoreUrl, page = 1) {
    let loading = false;
    let hasMore = true;
    
    window.addEventListener('scroll', debounce(function() {
        if (loading || !hasMore) return;
        
        const containerRect = container.getBoundingClientRect();
        if (containerRect.bottom <= window.innerHeight + 100) {
            loading = true;
            
            fetch(`${loadMoreUrl}?page=${page + 1}`)
                .then(response => response.json())
                .then(data => {
                    if (data.items && data.items.length > 0) {
                        container.insertAdjacentHTML('beforeend', data.html);
                        page++;
                    } else {
                        hasMore = false;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                })
                .finally(() => {
                    loading = false;
                });
        }
    }, 200));
} 