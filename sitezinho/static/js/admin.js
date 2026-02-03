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

function export_merged_image() {
  const button = document.querySelector('.export-btn');
  const originalText = button.querySelector('.button-title').textContent;
  
  // Show loading state
  button.disabled = true;
  button.classList.add('loading');
  button.querySelector('.button-title').textContent = 'Gerando Collage...';
  button.querySelector('span').textContent = '⏳';
  
  // Get export options
  const gap = document.getElementById('exportGap').value;
  const format = document.getElementById('exportFormat').value;
  const fixedSize = document.getElementById('fixedSize').checked;
  
  // Build URL with parameters
  let url = '/merged_image?';
  const params = new URLSearchParams();
  
  params.append('gap', gap);
  params.append('format', format);
  
  if (fixedSize) {
    const width = document.getElementById('exportWidth').value;
    const height = document.getElementById('exportHeight').value;
    params.append('width', width);
    params.append('height', height);
  }
  
  url += params.toString();
  
  // Create temporary link for download
  const link = document.createElement('a');
  link.href = url;
  link.style.display = 'none';
  document.body.appendChild(link);
  
  // Trigger download
  link.click();
  
  // Cleanup and reset button state
  setTimeout(() => {
    document.body.removeChild(link);
    button.disabled = false;
    button.classList.remove('loading');
    button.querySelector('.button-title').textContent = originalText;
    button.querySelector('span').textContent = '🎨';
    
    // Show success message
    showNotification('Collage gerada com sucesso!', 'success');
  }, 1000);
}

// Toggle function removed - options are now always visible

function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <span class="notification-icon">${type === 'success' ? '✅' : '📢'}</span>
    <span class="notification-message">${message}</span>
  `;
  
  // Add to page
  document.body.appendChild(notification);
  
  // Show animation
  setTimeout(() => notification.classList.add('show'), 100);
  
  // Remove after delay
  setTimeout(() => {
    notification.classList.remove('show');
    setTimeout(() => document.body.removeChild(notification), 300);
  }, 3000);
}

function delete_vote(id) {
 var json_vote = JSON.stringify(id)
  fetch('/delete_vote', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
    body: json_vote
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .then(() => location.reload())
  .catch(error => console.error('Error:', error));
}
window.delete_vote = delete_vote

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("delete_votes").addEventListener("click", delete_votes)
  document.getElementById("delete_images").addEventListener("click", delete_images)
  document.getElementById("export_merged_image").addEventListener("click", export_merged_image)
  document.getElementById("change_vote_unique").addEventListener("click", change_vote_unique)
  document.getElementById("change_vote_multiple").addEventListener("click", change_vote_multiple)
  document.getElementById("setVotePercentage").addEventListener("click", setVotePercentage)

  // Gap slider interaction
  const gapSlider = document.getElementById('exportGap');
  const gapValue = document.getElementById('gapValue');
  
  if (gapSlider && gapValue) {
    gapSlider.addEventListener('input', function() {
      gapValue.textContent = this.value + 'px';
    });
  }
  
  // Fixed size checkbox interaction
  const fixedSizeCheckbox = document.getElementById('fixedSize');
  const fixedSizeOptions = document.getElementById('fixedSizeOptions');
  
  if (fixedSizeCheckbox && fixedSizeOptions) {
    fixedSizeCheckbox.addEventListener('change', function() {
      fixedSizeOptions.style.display = this.checked ? 'block' : 'none';
    });
  }

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
})