import { initializePage } from "./utils.js";

let canvas, ctx, img, currentImage;
let scale = 1;
let offsetX = 0;
let offsetY = 0;
let isDragging = false;
let lastMouseX = 0;
let lastMouseY = 0;

function openModal(imageSrc, imageName) {
  const modal = document.getElementById('imageModal');
  const modalTitle = document.getElementById('modalTitle');
  
  // Setup canvas
  canvas = document.getElementById('imageCanvas');
  ctx = canvas.getContext('2d');
  
  // Configure canvas for high-quality rendering
  // Disable default image smoothing for initial setup
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = 'high';
  
  // Set modal title
  modalTitle.textContent = imageName;
  
  // Load and display image
  loadImageToCanvas(imageSrc);
  
  // Show modal
  modal.style.display = 'block';
  
  // Prevent body scroll when modal is open
  document.body.style.overflow = 'hidden';
  
  // Setup canvas event listeners
  setupCanvasEvents();
}

window.openModal = openModal

function loadImageToCanvas(imageSrc) {
  img = new Image();
  
  // Set crossOrigin to allow loading images from same domain
  img.crossOrigin = 'anonymous';
  
  img.onload = function() {
    currentImage = img;
    
    // Reset canvas configuration
    resetCanvas();
    
    // Initial draw with high quality
    drawImage();
  };
  
  // Handle loading errors
  img.onerror = function() {
    console.error('Failed to load image:', imageSrc);
    alert('Erro ao carregar a imagem. Tente novamente.');
  };
  
  img.src = imageSrc;
}

function resetCanvas() {
  // Set canvas size to container size
  const container = canvas.parentElement;
  const containerWidth = container.offsetWidth;
  const containerHeight = container.offsetHeight;
  
  // Get device pixel ratio for high-DPI displays (Retina, etc.)
  const pixelRatio = window.devicePixelRatio || 1;
  
  // Set actual canvas size accounting for device pixel ratio
  canvas.width = containerWidth * pixelRatio;
  canvas.height = containerHeight * pixelRatio;
  
  // Scale canvas back down using CSS for proper display size
  canvas.style.width = containerWidth + 'px';
  canvas.style.height = containerHeight + 'px';
  
  // Scale the drawing context to account for device pixel ratio
  ctx.scale(pixelRatio, pixelRatio);
  
  // Calculate initial scale to fit image (using CSS dimensions)
  const scaleX = containerWidth / img.width;
  const scaleY = containerHeight / img.height;
  scale = Math.min(scaleX, scaleY);
  
  // Center the image (using CSS dimensions)
  offsetX = (containerWidth - img.width * scale) / 2;
  offsetY = (containerHeight - img.height * scale) / 2;
  
  updateZoomLevel();
}

function drawImage() {
  // Clear canvas with proper dimensions
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Configure context for high-quality rendering
  ctx.save();
  
  // Disable image smoothing for crisp pixel-perfect rendering when zoomed in
  if (scale >= 1) {
    ctx.imageSmoothingEnabled = false;
  } else {
    // Enable high-quality smoothing for zoomed out images
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
  }
  
  // Draw image with current transform
  ctx.drawImage(img, offsetX, offsetY, img.width * scale, img.height * scale);
  
  ctx.restore();
}

function updateZoomLevel() {
  const zoomLevel = document.querySelector('.zoom-level');
  zoomLevel.textContent = Math.round(scale * 100) + '%';
}

function setupCanvasEvents() {
  // Mouse wheel zoom
  canvas.addEventListener('wheel', function(e) {
    e.preventDefault();
    
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = scale * zoomFactor;
    
    // Limit zoom levels
    if (newScale < 0.1 || newScale > 5) return;
    
    // Zoom towards mouse position
    offsetX = mouseX - (mouseX - offsetX) * (newScale / scale);
    offsetY = mouseY - (mouseY - offsetY) * (newScale / scale);
    
    scale = newScale;
    updateZoomLevel();
    drawImage();
  });
  
  // Mouse drag to pan
  canvas.addEventListener('mousedown', function(e) {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
    canvas.style.cursor = 'grabbing';
  });
  
  canvas.addEventListener('mousemove', function(e) {
    if (isDragging) {
      const deltaX = e.clientX - lastMouseX;
      const deltaY = e.clientY - lastMouseY;
      
      offsetX += deltaX;
      offsetY += deltaY;
      
      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
      
      drawImage();
    }
  });
  
  canvas.addEventListener('mouseup', function() {
    isDragging = false;
    canvas.style.cursor = 'grab';
  });
  
  canvas.addEventListener('mouseleave', function() {
    isDragging = false;
    canvas.style.cursor = 'grab';
  });
  
  // Touch events for mobile
  let lastTouchX = 0;
  let lastTouchY = 0;
  
  canvas.addEventListener('touchstart', function(e) {
    e.preventDefault();
    const touch = e.touches[0];
    lastTouchX = touch.clientX;
    lastTouchY = touch.clientY;
    isDragging = true;
  });
  
  canvas.addEventListener('touchmove', function(e) {
    e.preventDefault();
    if (isDragging && e.touches.length === 1) {
      const touch = e.touches[0];
      const deltaX = touch.clientX - lastTouchX;
      const deltaY = touch.clientY - lastTouchY;
      
      offsetX += deltaX;
      offsetY += deltaY;
      
      lastTouchX = touch.clientX;
      lastTouchY = touch.clientY;
      
      drawImage();
    }
  });
  
  canvas.addEventListener('touchend', function(e) {
    e.preventDefault();
    isDragging = false;
  });
}

document.addEventListener('DOMContentLoaded', function() {
  // Initialize page state (clear checkboxes, etc.)
  initializePage();
  const modal = document.getElementById('imageModal');
  const closeBtn = document.querySelector('.close-modal');
  
  // Close modal when clicking the X button
  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal);
  }
  
  // Close modal when clicking outside the image
  if (modal) {
    modal.addEventListener('click', function(event) {
      if (event.target === modal) {
        closeModal();
      }
    });
  }
  
 
  
  // Close modal with ESC key
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      closeModal();
    }
  });
  
  // Canvas control buttons
  const zoomInBtn = document.getElementById('zoomIn');
  const zoomOutBtn = document.getElementById('zoomOut');
  const resetZoomBtn = document.getElementById('resetZoom');
  const fitToScreenBtn = document.getElementById('fitToScreen');
  
  if (zoomInBtn) {
    zoomInBtn.addEventListener('click', function() {
      if (canvas && currentImage) {
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const newScale = scale * 1.2;
        
        if (newScale <= 5) {
          offsetX = centerX - (centerX - offsetX) * (newScale / scale);
          offsetY = centerY - (centerY - offsetY) * (newScale / scale);
          scale = newScale;
          updateZoomLevel();
          drawImage();
        }
      }
    });
  }
  
  if (zoomOutBtn) {
    zoomOutBtn.addEventListener('click', function() {
      if (canvas && currentImage) {
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const newScale = scale * 0.8;
        
        if (newScale >= 0.1) {
          offsetX = centerX - (centerX - offsetX) * (newScale / scale);
          offsetY = centerY - (centerY - offsetY) * (newScale / scale);
          scale = newScale;
          updateZoomLevel();
          drawImage();
        }
      }
    });
  }
  
  if (resetZoomBtn) {
    resetZoomBtn.addEventListener('click', function() {
      if (canvas && currentImage) {
        resetCanvas();
        drawImage();
      }
    });
  }
  
  if (fitToScreenBtn) {
    fitToScreenBtn.addEventListener('click', function() {
      if (canvas && currentImage) {
        // Fit to screen with some padding
        const padding = 20;
        const scaleX = (canvas.width - padding * 2) / img.width;
        const scaleY = (canvas.height - padding * 2) / img.height;
        scale = Math.min(scaleX, scaleY);
        
        offsetX = (canvas.width - img.width * scale) / 2;
        offsetY = (canvas.height - img.height * scale) / 2;
        
        updateZoomLevel();
        drawImage();
      }
    });
  }
});

function closeModal() {
  const modal = document.getElementById('imageModal');
  modal.style.display = 'none';
  
  // Restore body scroll
  document.body.style.overflow = 'auto';
  
  // Clear canvas event listeners
  if (canvas) {
    canvas.removeEventListener('wheel', null);
    canvas.removeEventListener('mousedown', null);
    canvas.removeEventListener('mousemove', null);
    canvas.removeEventListener('mouseup', null);
    canvas.removeEventListener('mouseleave', null);
    canvas.removeEventListener('touchstart', null);
    canvas.removeEventListener('touchmove', null);
    canvas.removeEventListener('touchend', null);
  }
}
