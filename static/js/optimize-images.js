/**
 * Rule Ready Image Optimization and Responsive Images
 * 
 * This script enhances image loading by:
 * 1. Implementing lazy loading for images
 * 2. Setting up responsive image srcsets
 * 3. Applying WebP format where supported
 */

class ImageOptimizer {
    constructor() {
        this.supportsWebP = false;
        this.initialized = false;
    }

    /**
     * Initialize the image optimizer
     */
    async init() {
        if (this.initialized) return;
        
        // Check for WebP support
        this.supportsWebP = await this.checkWebPSupport();
        
        // Process images on the page
        this.setupLazyLoading();
        this.makeImagesResponsive();
        
        this.initialized = true;
    }

    /**
     * Check if the browser supports WebP format
     */
    async checkWebPSupport() {
        // Try creating a WebP image
        const webPCheck = new Promise(resolve => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = 'data:image/webp;base64,UklGRhoAAABXRUJQVlA4TA0AAAAvAAAAEAcQERGIiP4HAA==';
        });
        
        return await webPCheck;
    }

    /**
     * Set up lazy loading for images
     */
    setupLazyLoading() {
        // Find all images that could be lazy loaded
        const images = document.querySelectorAll('img:not([loading])');
        
        images.forEach(img => {
            // Add loading attribute
            img.setAttribute('loading', 'lazy');
            
            // Store original src
            const originalSrc = img.getAttribute('src');
            if (originalSrc && !img.getAttribute('data-src')) {
                img.setAttribute('data-src', originalSrc);
                
                // Set a placeholder or low-res image first
                img.setAttribute('src', 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3C/svg%3E');
            }
        });
        
        // Set up intersection observer for lazy loading
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const image = entry.target;
                        const dataSrc = image.getAttribute('data-src');
                        
                        if (dataSrc) {
                            image.setAttribute('src', dataSrc);
                            image.removeAttribute('data-src');
                        }
                        
                        observer.unobserve(image);
                    }
                });
            });
            
            images.forEach(image => {
                imageObserver.observe(image);
            });
        } else {
            // Fallback for browsers that don't support IntersectionObserver
            images.forEach(image => {
                const dataSrc = image.getAttribute('data-src');
                if (dataSrc) {
                    image.setAttribute('src', dataSrc);
                    image.removeAttribute('data-src');
                }
            });
        }
    }

    /**
     * Make images responsive by adding srcset and sizes attributes
     */
    makeImagesResponsive() {
        const images = document.querySelectorAll('img:not([srcset])');
        
        images.forEach(img => {
            // Don't process images that already have srcset or are from external domains
            if (img.hasAttribute('srcset') || (img.src && img.src.indexOf('http') === 0 && !img.src.includes(window.location.hostname))) {
                return;
            }
            
            const src = img.getAttribute('data-src') || img.getAttribute('src');
            if (!src || src.startsWith('data:')) return;
            
            // Create srcset for various sizes
            // This requires proper backend support for generating different image sizes
            // Example: If src is "image.jpg", we'd need "image-300w.jpg", "image-600w.jpg", etc.
            const baseName = src.substring(0, src.lastIndexOf('.'));
            const extension = src.substring(src.lastIndexOf('.'));
            
            // We'll need server-side support to actually have these different sized images
            // This is a placeholder for how it would work
            const srcset = [
                `${baseName}-300w${extension} 300w`,
                `${baseName}-600w${extension} 600w`,
                `${baseName}-900w${extension} 900w`,
                `${baseName}${extension} 1200w`,
            ].join(', ');
            
            img.setAttribute('srcset', srcset);
            
            // Set appropriate sizes attribute
            const sizes = img.hasAttribute('sizes') 
                ? img.getAttribute('sizes') 
                : '(max-width: 576px) 100vw, (max-width: 768px) 50vw, 33vw';
            
            img.setAttribute('sizes', sizes);
            
            // If WebP is supported, add a picture element with WebP source
            if (this.supportsWebP && img.parentNode.tagName !== 'PICTURE') {
                const picture = document.createElement('picture');
                const source = document.createElement('source');
                
                // Set WebP srcset (requires server-side support)
                const webPSrcset = [
                    `${baseName}-300w.webp 300w`,
                    `${baseName}-600w.webp 600w`,
                    `${baseName}-900w.webp 900w`,
                    `${baseName}.webp 1200w`,
                ].join(', ');
                
                source.setAttribute('srcset', webPSrcset);
                source.setAttribute('sizes', sizes);
                source.setAttribute('type', 'image/webp');
                
                // Replace the image with a picture element
                const parent = img.parentNode;
                picture.appendChild(source);
                
                // Move the original img to be inside the picture
                parent.replaceChild(picture, img);
                picture.appendChild(img);
            }
        });
    }
}

// Initialize the image optimizer on page load
document.addEventListener('DOMContentLoaded', () => {
    const imageOptimizer = new ImageOptimizer();
    imageOptimizer.init();
}); 