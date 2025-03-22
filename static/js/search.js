/**
 * Rule Ready Search Functionality
 * 
 * Provides site-wide search capabilities for finding rules and quiz content
 */

class RuleReadySearch {
    constructor() {
        this.searchIndex = {};
        this.searchResults = [];
        this.initialized = false;
    }

    /**
     * Initialize search functionality
     */
    init() {
        if (this.initialized) return;

        // Add search UI to the navigation
        this.addSearchUI();
        
        // Build search index
        this.buildSearchIndex();
        
        // Add event listeners
        this.bindEvents();
        
        this.initialized = true;
    }

    /**
     * Add search UI to the navigation bar
     */
    addSearchUI() {
        const navbarNav = document.querySelector('#navbarNav ul.navbar-nav');
        if (!navbarNav) return;

        const searchHTML = `
            <li class="nav-item me-2">
                <div class="search-container">
                    <input type="text" class="form-control search-input" placeholder="Search rules..." 
                           aria-label="Search" id="siteSearch">
                    <div class="search-results-container" id="searchResults"></div>
                </div>
            </li>
        `;
        
        navbarNav.insertAdjacentHTML('beforebegin', searchHTML);
        
        // Add search styles
        const style = document.createElement('style');
        style.textContent = `
            .search-container {
                position: relative;
                min-width: 200px;
            }
            .search-input {
                border-radius: 20px;
                padding-left: 15px;
                min-height: 38px;
            }
            .search-results-container {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: white;
                border-radius: 4px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                max-height: 300px;
                overflow-y: auto;
                z-index: 1000;
                display: none;
            }
            .search-results-container.show {
                display: block;
            }
            .search-result-item {
                padding: 8px 15px;
                border-bottom: 1px solid #eee;
                cursor: pointer;
            }
            .search-result-item:hover {
                background-color: #f5f5f5;
            }
            .search-result-item .title {
                font-weight: 600;
                color: #2c3e50;
            }
            .search-result-item .context {
                font-size: 0.85rem;
                color: #666;
            }
            .highlight {
                background-color: #ffe68550;
                padding: 0 2px;
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Build a search index from the page content
     */
    buildSearchIndex() {
        // Start by requesting the rules JSON
        fetch('/api/rules')
            .then(response => response.json())
            .then(data => {
                // Index rules content
                if (data && data.rules) {
                    data.rules.forEach(rule => {
                        this.searchIndex[`rule-${rule.number}`] = {
                            title: `Rule ${rule.number}: ${rule.title}`,
                            content: rule.content,
                            url: `/rules#rule-${rule.number}`
                        };
                    });
                }
            })
            .catch(err => console.error('Error loading rules for search:', err));
    }

    /**
     * Bind event listeners for search functionality
     */
    bindEvents() {
        const searchInput = document.getElementById('siteSearch');
        const resultsContainer = document.getElementById('searchResults');
        
        if (!searchInput || !resultsContainer) return;
        
        // Search on input
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();
            
            if (query.length < 2) {
                resultsContainer.classList.remove('show');
                return;
            }
            
            this.performSearch(query);
            
            // Display results
            if (this.searchResults.length > 0) {
                this.displayResults(resultsContainer, query);
                resultsContainer.classList.add('show');
            } else {
                resultsContainer.innerHTML = `<div class="search-result-item">No results found for "${query}"</div>`;
                resultsContainer.classList.add('show');
            }
        });
        
        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.classList.remove('show');
            }
        });
        
        // Clear on escape key
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                searchInput.value = '';
                resultsContainer.classList.remove('show');
            }
        });
    }

    /**
     * Perform search against the index
     */
    performSearch(query) {
        this.searchResults = [];
        const queryLower = query.toLowerCase();
        
        // Search through the index
        for (const id in this.searchIndex) {
            const item = this.searchIndex[id];
            const titleLower = item.title.toLowerCase();
            const contentLower = item.content.toLowerCase();
            
            if (titleLower.includes(queryLower) || contentLower.includes(queryLower)) {
                // Find the context around the match
                let context = '';
                const contentIndex = contentLower.indexOf(queryLower);
                if (contentIndex !== -1) {
                    const start = Math.max(0, contentIndex - 40);
                    const end = Math.min(item.content.length, contentIndex + query.length + 40);
                    context = item.content.substring(start, end);
                    
                    // Add ellipsis if needed
                    if (start > 0) context = '...' + context;
                    if (end < item.content.length) context = context + '...';
                }
                
                this.searchResults.push({
                    id,
                    title: item.title,
                    context: context || item.content.substring(0, 100) + '...',
                    url: item.url
                });
            }
        }
    }

    /**
     * Display search results in the container
     */
    displayResults(container, query) {
        container.innerHTML = '';
        
        this.searchResults.slice(0, 5).forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'search-result-item';
            
            // Highlight the query in the title and context
            const highlightedTitle = this.highlightQuery(result.title, query);
            const highlightedContext = this.highlightQuery(result.context, query);
            
            resultItem.innerHTML = `
                <div class="title">${highlightedTitle}</div>
                <div class="context">${highlightedContext}</div>
            `;
            
            resultItem.addEventListener('click', () => {
                window.location.href = result.url;
            });
            
            container.appendChild(resultItem);
        });
    }

    /**
     * Highlight query terms in text
     */
    highlightQuery(text, query) {
        const queryLower = query.toLowerCase();
        const textLower = text.toLowerCase();
        
        let result = text;
        let index = textLower.indexOf(queryLower);
        
        if (index !== -1) {
            const matchedText = text.substring(index, index + query.length);
            result = text.replace(
                new RegExp(matchedText, 'gi'), 
                match => `<span class="highlight">${match}</span>`
            );
        }
        
        return result;
    }
}

// Initialize search on page load
document.addEventListener('DOMContentLoaded', () => {
    const search = new RuleReadySearch();
    search.init();
}); 