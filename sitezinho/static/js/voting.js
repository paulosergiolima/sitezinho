function clearAllCheckboxes() {
  const checkboxes = document.querySelectorAll("input[type='checkbox']");
  checkboxes.forEach(checkbox => {
    checkbox.checked = false;
    // Force trigger change event to update any UI that depends on checkbox state
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
  });
}
  console.log('All checkboxes cleared');
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