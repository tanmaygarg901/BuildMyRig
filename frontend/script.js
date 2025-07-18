// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const buildForm = document.getElementById('buildForm');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const partsContainer = document.getElementById('partsContainer');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupNavigation();
    loadDefaultParts();
});

// Setup event listeners
function setupEventListeners() {
    buildForm.addEventListener('submit', handleBuildFormSubmit);
    
    // Parts tab buttons
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', handleTabClick);
    });
}

// Setup smooth scrolling navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
            
            // Update active nav link
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

// Handle build form submission
async function handleBuildFormSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(buildForm);
    const budget = parseFloat(formData.get('budget'));
    const useCase = formData.get('useCase');
    const cpuBrand = formData.get('cpuBrand');
    const gpuBrand = formData.get('gpuBrand');
    
    // Validate form
    if (!budget || !useCase) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    // Prepare request data
    const requestData = {
        budget: budget,
        use_case: useCase,
        brand_preferences: {}
    };
    
    if (cpuBrand) requestData.brand_preferences.cpu = cpuBrand;
    if (gpuBrand) requestData.brand_preferences.gpu = gpuBrand;
    
    // Show loading state
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        displayResults(data);
        showToast('Build recommendations found!', 'success');
        
    } catch (error) {
        console.error('Error fetching recommendations:', error);
        hideLoading();
        showToast('Failed to get recommendations. Please try again.', 'error');
    }
}

// Show loading state
function showLoading() {
    loadingSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    
    // Scroll to loading section
    loadingSection.scrollIntoView({
        behavior: 'smooth',
        block: 'center'
    });
}

// Hide loading state
function hideLoading() {
    loadingSection.classList.add('hidden');
}

// Display build results
function displayResults(data) {
    hideLoading();
    
    resultsContainer.innerHTML = '';
    
    if (data.builds && data.builds.length > 0) {
        data.builds.forEach((build, index) => {
            const buildCard = createBuildCard(build, index + 1);
            resultsContainer.appendChild(buildCard);
        });
        
        resultsSection.classList.remove('hidden');
        
        // Scroll to results
        resultsSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    } else {
        showToast('No builds found for your criteria', 'error');
    }
}

// Create build card element
function createBuildCard(build, buildNumber) {
    const card = document.createElement('div');
    card.className = 'build-card';
    
    const partsList = build.parts.map(part => {
        return `
            <div class="part-item">
                <div class="part-info">
                    <span class="part-category">${part.category}</span>
                    <span class="part-name">${part.name}</span>
                </div>
                <span class="part-price">$${part.price}</span>
            </div>
        `;
    }).join('');
    
    card.innerHTML = `
        <div class="build-header">
            <h3 class="build-title">Build ${buildNumber}</h3>
            <span class="build-price">$${build.total_price}</span>
        </div>
        <div class="build-score">
            Bang-for-Buck Score: ${build.bang_for_buck_score}
        </div>
        <div class="parts-list">
            ${partsList}
        </div>
    `;
    
    return card;
}

// Handle parts tab clicks
function handleTabClick(e) {
    const category = e.target.dataset.category;
    
    // Update active tab
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    e.target.classList.add('active');
    
    // Load parts for category
    loadPartsByCategory(category);
}

// Load parts by category with pagination and sorting
async function loadPartsByCategory(category, limit = 20, offset = 0, sortBy = 'performance_score', sortOrder = 'desc') {
    try {
        partsContainer.innerHTML = '<div class="loading-parts">Loading parts...</div>';
        
        const params = new URLSearchParams({
            limit: limit.toString(),
            offset: offset.toString(),
            sort_by: sortBy,
            sort_order: sortOrder
        });
        
        const response = await fetch(`${API_BASE_URL}/parts/${category}?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const parts = await response.json();
        displayParts(parts, category);
        
    } catch (error) {
        console.error('Error loading parts:', error);
        partsContainer.innerHTML = '<div class="error-message">Failed to load parts</div>';
    }
}

// Display parts in the container with sorting controls
function displayParts(parts, category) {
    partsContainer.innerHTML = '';
    
    if (parts.length === 0) {
        partsContainer.innerHTML = '<div class="no-parts">No parts found in this category</div>';
        return;
    }
    
    // Add sorting controls
    const sortingControls = document.createElement('div');
    sortingControls.className = 'sorting-controls';
    sortingControls.innerHTML = `
        <div class="sort-options">
            <label for="sortBy">Sort by:</label>
            <select id="sortBy">
                <option value="performance_score">Performance (High to Low)</option>
                <option value="price">Price (Low to High)</option>
                <option value="name">Name (A to Z)</option>
            </select>
        </div>
        <div class="results-info">
            Showing ${parts.length} parts
        </div>
    `;
    
    partsContainer.appendChild(sortingControls);
    
    // Add event listener for sorting
    const sortSelect = sortingControls.querySelector('#sortBy');
    sortSelect.addEventListener('change', function() {
        const sortBy = this.value;
        const sortOrder = sortBy === 'price' || sortBy === 'name' ? 'asc' : 'desc';
        loadPartsByCategory(category, 20, 0, sortBy, sortOrder);
    });
    
    // Create parts grid
    const partsGrid = document.createElement('div');
    partsGrid.className = 'parts-grid';
    
    parts.forEach(part => {
        const partCard = createPartCard(part);
        partsGrid.appendChild(partCard);
    });
    
    partsContainer.appendChild(partsGrid);
    
    // Add load more button if we received the full limit (indicating there might be more)
    if (parts.length >= 20) {
        const loadMoreBtn = document.createElement('button');
        loadMoreBtn.className = 'load-more-btn';
        loadMoreBtn.textContent = 'Load More Parts';
        loadMoreBtn.addEventListener('click', function() {
            loadMoreParts(category, parts.length);
        });
        partsContainer.appendChild(loadMoreBtn);
    }
}

// Create part card element
function createPartCard(part) {
    const card = document.createElement('div');
    card.className = 'part-card';
    
    card.innerHTML = `
        <div class="part-card-header">
            <div>
                <h4 class="part-card-title">${part.name}</h4>
                <span class="part-card-brand">${part.brand}</span>
            </div>
            <span class="part-card-price">$${part.price}</span>
        </div>
        <div class="part-card-score">
            Performance: ${part.performance_score}
        </div>
    `;
    
    return card;
}

// Load more parts (append to existing parts)
async function loadMoreParts(category, currentOffset) {
    try {
        const loadMoreBtn = document.querySelector('.load-more-btn');
        loadMoreBtn.textContent = 'Loading...';
        loadMoreBtn.disabled = true;
        
        const params = new URLSearchParams({
            limit: '20',
            offset: currentOffset.toString(),
            sort_by: 'performance_score',
            sort_order: 'desc'
        });
        
        const response = await fetch(`${API_BASE_URL}/parts/${category}?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const newParts = await response.json();
        
        // Remove the old load more button
        loadMoreBtn.remove();
        
        // Add new parts to the grid
        const partsGrid = document.querySelector('.parts-grid');
        newParts.forEach(part => {
            const partCard = createPartCard(part);
            partsGrid.appendChild(partCard);
        });
        
        // Update results info
        const resultsInfo = document.querySelector('.results-info');
        const totalShown = currentOffset + newParts.length;
        resultsInfo.textContent = `Showing ${totalShown} parts`;
        
        // Add new load more button if we received the full limit
        if (newParts.length >= 20) {
            const newLoadMoreBtn = document.createElement('button');
            newLoadMoreBtn.className = 'load-more-btn';
            newLoadMoreBtn.textContent = 'Load More Parts';
            newLoadMoreBtn.addEventListener('click', function() {
                loadMoreParts(category, totalShown);
            });
            partsContainer.appendChild(newLoadMoreBtn);
        }
        
    } catch (error) {
        console.error('Error loading more parts:', error);
        showToast('Failed to load more parts', 'error');
        
        // Re-enable the button
        const loadMoreBtn = document.querySelector('.load-more-btn');
        if (loadMoreBtn) {
            loadMoreBtn.textContent = 'Load More Parts';
            loadMoreBtn.disabled = false;
        }
    }
}

// Load default parts (CPU category)
function loadDefaultParts() {
    loadPartsByCategory('cpu');
}

// Show toast notification
function showToast(message, type = 'success') {
    toastMessage.textContent = message;
    
    // Update toast styling based on type
    if (type === 'error') {
        toast.style.background = '#ef4444';
    } else {
        toast.style.background = '#059669';
    }
    
    toast.classList.add('show');
    
    // Hide toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Smooth scroll to form
function scrollToForm() {
    const formSection = document.querySelector('.build-form-section');
    formSection.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to capitalize first letter
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Handle window scroll for navigation highlighting
window.addEventListener('scroll', function() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let currentSection = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.offsetHeight;
        
        if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
            currentSection = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
});

// Handle form validation
function validateForm() {
    const budget = document.getElementById('budget').value;
    const useCase = document.getElementById('useCase').value;
    
    if (!budget || budget < 500) {
        showToast('Please enter a budget of at least $500', 'error');
        return false;
    }
    
    if (!useCase) {
        showToast('Please select a use case', 'error');
        return false;
    }
    
    return true;
}

// Add some interactive feedback
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Add focus effects to form inputs
    const inputs = document.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });
});

// Error handling for API calls
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showToast('An unexpected error occurred. Please try again.', 'error');
});

// Check API connection on page load
async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('API connection successful');
        } else {
            showToast('API connection failed. Please ensure the backend is running.', 'error');
        }
    } catch (error) {
        console.error('API connection check failed:', error);
        showToast('Cannot connect to API. Please ensure the backend is running on localhost:8000.', 'error');
    }
}

// Initialize API connection check
document.addEventListener('DOMContentLoaded', checkAPIConnection);
