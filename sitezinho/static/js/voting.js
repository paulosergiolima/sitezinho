import { clearAllCheckboxes } from "./utils.js";

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

let single_vote = window.VOTE_CONFIG?.single_vote || false;

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


document.addEventListener('DOMContentLoaded', function() {
  var vote_button = document.getElementById("vote")
  vote_button.addEventListener('click', vote)
})