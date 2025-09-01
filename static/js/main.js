// Global variables for vote configuration (set by template)
let single_vote = false;
let vote_percentage = 50;
let total_images = 0;
let max_votes = 1;

/**
 * Force clear all checkboxes - especially useful for mobile browsers
 * that might cache form states after reload
 */
function clearAllCheckboxes() {
  const checkboxes = document.querySelectorAll("input[type='checkbox']");
  checkboxes.forEach(checkbox => {
    checkbox.checked = false;
    // Force trigger change event to update any UI that depends on checkbox state
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
  });
  
  console.log('All checkboxes cleared');
}

/**
 * Initialize page state - ensure clean slate on page load
 */
function initializePage() {
  // Clear all checkboxes on page load (mobile cache fix)
  clearAllCheckboxes();
  
  // Verify checkboxes are actually cleared
  const checkedBoxes = document.querySelectorAll("input[type='checkbox']:checked");
  if (checkedBoxes.length > 0) {
    console.warn(`Warning: ${checkedBoxes.length} checkboxes still checked after initialization`);
    // Force clear again if needed
    checkedBoxes.forEach(box => box.checked = false);
  }
  
  console.log('Page initialized - all checkboxes cleared');
  
  // Update vote counter if in multiple choice mode
  if (typeof updateVoteCounter === 'function') {
    updateVoteCounter();
  }
}
async function vote() {
  try {
    const username = prompt("Qual seu usuário?");
    
    // Check if username was provided
    if (!username || username.trim() === '') {
      alert("Nome de usuário é obrigatório!");
      return;
    }

    if (username.length > 50) {
      alert("Nome de usuário deve ter menos de 50 caracteres!");
      return;
    }

    // Check if user has already voted
    const checkResponse = await fetch('/check_user', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username: username.trim() })
    });

    const checkResult = await checkResponse.json();
    
    if (checkResult.has_voted) {
      alert(`O usuário "${username}" já votou! Cada pessoa pode votar apenas uma vez.`);
      return;
    }

    // Collect votes
    const votes = [];
    const inputs = document.querySelectorAll("input[type='checkbox']");
    for (let i = 0; i < inputs.length; i++) {
      if (inputs[i].checked === true) {
        votes.push(inputs[i].name);
      }
    }

    // Check if at least one vote was selected
    if (votes.length === 0) {
      alert("Selecione pelo menos uma opção para votar!");
      return;
    }

    const json_votes = JSON.stringify([username.trim(), votes]);

    const voteResponse = await fetch('/vote', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: json_votes
    });

    const result = await voteResponse.json();
    console.log(result);

    // Check if vote was successful
    if (result.success) {
      alert("Seu voto foi contabilizado");
      
      // Force clear all checkboxes before reload (mobile fix)
      clearAllCheckboxes();
      
      // Add a small delay to ensure checkbox clearing is processed
      setTimeout(() => {
        window.location.reload();
      }, 100);
    } else {
      alert(`Erro: ${result.error || 'Não foi possível registrar o voto'}`);
      return;
    }

  } catch (error) {
    console.error('Error:', error);
    alert("Erro ao votar. Tente novamente.");
    
    // Clear checkboxes even on error (mobile fix)
    clearAllCheckboxes();
    
    // Reload even on error to reset form state
    setTimeout(() => {
      window.location.reload();
    }, 100);
  }
}


function delete_votes() {
  // Confirm before deleting all votes
  if (!confirm('Tem certeza que deseja apagar TODOS os votos? Esta ação não pode ser desfeita!')) {
    return;
  }

  const button = event.target.closest('.control-button');
  
  fetch('/delete', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    if (data.success) {
      showButtonFeedback(button, true);
      alert('Todos os votos foram apagados com sucesso! ✅');
    } else {
      showButtonFeedback(button, false);
      alert('Erro ao apagar votos. Tente novamente.');
    }
    
    // Reload page after a short delay to show feedback first
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  })
  .catch(error => {
    console.error('Error:', error);
    showButtonFeedback(button, false);
    alert('Erro ao apagar votos. Tente novamente.');
    
    // Still reload on error to ensure UI consistency
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  });
}

function delete_images() {
  // Confirm before deleting all images
  if (!confirm('Tem certeza que deseja remover TODAS as imagens? Esta ação não pode ser desfeita!')) {
    return;
  }
  
  const button = event.target.closest('.control-button');
  
  fetch('/delete_images', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    if (data.success) {
      showButtonFeedback(button, true);
      alert(`${data.deleted_count} imagens foram removidas com sucesso! ✅`);
    } else {
      showButtonFeedback(button, false);
      alert(`Erro ao remover imagens: ${data.error}`);
    }
    
    // Reload page after a short delay to show feedback first
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  })
  .catch(error => {
    console.error('Error:', error);
    showButtonFeedback(button, false);
    alert('Erro ao remover imagens. Tente novamente.');
    
    // Still reload on error to ensure UI consistency
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  });
}

if (single_vote == true) {
  $("input:checkbox").on('click', function() {
    // in the handler, 'this' refers to the box clicked on
    var $box = $(this);
    if ($box.is(":checked")) {
      // the name of the box is retrieved using the .attr() method
      // as it is assumed and expected to be immutable
      var group = "input:checkbox[name='" + $box.attr("name") + "']";
      // the checked state of the group/box on the other hand will change
      // and the current value is retrieved using .prop() method
      $(group).prop("checked", false);
      $box.prop("checked", true);
    } else {
      $box.prop("checked", false);
    }
  });
}

function showButtonFeedback(button, success = true, customMessage = '') {
  const originalText = button.querySelector('.button-title').textContent;
  
  // Remove any existing feedback classes
  button.classList.remove('feedback-success', 'feedback-error');
  
  if (success) {
    button.classList.add('feedback-success');
    
    // Use custom message or determine based on button type
    let message = customMessage;
    if (!message) {
      if (originalText.includes('Limpar Votos')) {
        message = '✅ Votos Apagados!';
      } else if (originalText.includes('Remover Imagens')) {
        message = '✅ Imagens Removidas!';
      } else {
        message = '✅ Alterado!';
      }
    }
    button.querySelector('.button-title').textContent = message;
  } else {
    button.classList.add('feedback-error');
    button.querySelector('.button-title').textContent = customMessage || '❌ Erro';
  }
  
  // Reset after 2.5 seconds
  setTimeout(() => {
    button.classList.remove('feedback-success', 'feedback-error');
    button.querySelector('.button-title').textContent = originalText;
  }, 2500);
}

function change_vote_unique() {
  const button = event.target.closest('.control-button');
  
  fetch('/change_vote_unique', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    if (data.success) {
      showButtonFeedback(button, true);
      alert('Modo alterado para: Escolha Única ✅\nCada usuário poderá votar em apenas uma arte.');
    } else {
      showButtonFeedback(button, false);
      alert('Erro ao alterar modo de votação. Tente novamente.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showButtonFeedback(button, false);
    alert('Erro ao alterar modo de votação. Tente novamente.');
  });
}

function change_vote_multiple() {
  const button = event.target.closest('.control-button');
  
  fetch('/change_vote_multiple', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    if (data.success) {
      showButtonFeedback(button, true);
      alert('Modo alterado para: Múltipla Escolha ✅\nCada usuário poderá votar em várias artes.');
    } else {
      showButtonFeedback(button, false);
      alert('Erro ao alterar modo de votação. Tente novamente.');
    }
  })
  .catch(error => {
    console.error('Error:', error);
    showButtonFeedback(button, false);
    alert('Erro ao alterar modo de votação. Tente novamente.');
  });
}

function setVotePercentage() {
  const percentageInput = document.getElementById('votePercentage');
  const percentage = parseInt(percentageInput.value);
  
  // Validate input
  if (isNaN(percentage) || percentage < 1 || percentage > 100) {
    alert('Por favor, insira uma porcentagem válida entre 1 e 100.');
    return;
  }
  
  fetch('/set_vote_percentage', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ percentage: percentage })
  })
  .then(response => response.json())
  .then(data => {
    console.log(data);
    if (data.success) {
      // Update display
      const maxVotesDisplay = document.getElementById('maxVotesDisplay');
      const totalImages = parseInt(document.querySelector('.percentage-info small').textContent.match(/de (\d+)/)[1]);
      const maxVotes = Math.ceil((totalImages * percentage) / 100);
      
      if (maxVotesDisplay) {
        maxVotesDisplay.textContent = maxVotes;
      }
      
      // Update info text
      const infoElement = document.querySelector('.percentage-info small');
      if (infoElement) {
        infoElement.innerHTML = `Atual: <strong>${percentage}%</strong> (máximo <span id="maxVotesDisplay">${maxVotes}</span> votos de ${totalImages} imagens)`;
      }
      
      alert(`Porcentagem alterada para ${percentage}% ✅\nCada usuário poderá votar em até ${maxVotes} imagens.`);
    } else {
      alert(`Erro ao alterar porcentagem: ${data.error}`);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('Erro ao alterar porcentagem. Tente novamente.');
  });
}

function delete_vote(id) {
  json_vote = JSON.stringify(id)
  fetch('/delete_vote', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
    body: json_vote
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .then(data => location.reload())
  .catch(error => console.error('Error:', error));
}


// Canvas-based modal functionality for full view images
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

// Initialize page and modal event listeners when page loads
document.addEventListener('DOMContentLoaded', function() {
  // Initialize page state (clear checkboxes, etc.)
  initializePage();
  const modal = document.getElementById('imageModal');
  const closeBtn = document.querySelector('.close-modal');
  const modalImage = document.getElementById('modalImage');
  
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

// Admin page file input enhancement
document.addEventListener('DOMContentLoaded', function() {
  const fileInput = document.getElementById('file');
  const fileInfo = document.getElementById('fileInfo');
  
  if (fileInput && fileInfo) {
    fileInput.addEventListener('change', function(e) {
      const files = e.target.files;
      
      if (files.length === 0) {
        fileInfo.textContent = '';
        return;
      }
      
      if (files.length === 1) {
        fileInfo.textContent = `📄 Arquivo selecionado: ${files[0].name}`;
      } else {
        fileInfo.textContent = `📄 ${files.length} arquivos selecionados`;
      }
    });
  }
});

/**
 * Toggle the visibility of voters list for a specific image
 * @param {string} votersId - The ID of the voters list element to toggle
 */
function toggleVoters(votersId) {
  const votersElement = document.getElementById(votersId);
  
  if (!votersElement) {
    console.error(`Element with ID ${votersId} not found`);
    return;
  }
  
  // Hide all other voters lists first
  const allVotersLists = document.querySelectorAll('.voters-list');
  allVotersLists.forEach(list => {
    if (list.id !== votersId && list.style.display === 'block') {
      list.style.display = 'none';
    }
  });
  
  // Toggle the current voters list
  if (votersElement.style.display === 'none' || votersElement.style.display === '') {
    votersElement.style.display = 'block';
    
    // Add smooth animation
    votersElement.style.opacity = '0';
    votersElement.style.transform = 'translateY(-10px)';
    
    setTimeout(() => {
      votersElement.style.transition = 'all 0.3s ease';
      votersElement.style.opacity = '1';
      votersElement.style.transform = 'translateY(0)';
    }, 10);
  } else {
    votersElement.style.opacity = '0';
    votersElement.style.transform = 'translateY(-10px)';
    
    setTimeout(() => {
      votersElement.style.display = 'none';
      votersElement.style.transition = '';
    }, 300);
  }
}