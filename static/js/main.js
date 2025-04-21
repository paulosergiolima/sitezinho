single_vote = false
async function vote() {
  try {
    const checkResponse = await fetch('/voted');
    console.log(checkResponse)
    const alreadyVoted = await checkResponse.json();
    console.log(alreadyVoted)

    console.log('Flag is:', alreadyVoted);

    if (alreadyVoted.voted) {
      console.log("hi")
      //alert("Seu voto não vai ser contabilizado, por votar mais de uma vez");
      //return;
    }

    // Only ask for username if user can vote
    const username = prompt("Qual seu usuário?");
    const votes = [];

    const inputs = document.querySelectorAll("input[type='checkbox']");
    for (let i = 0; i < inputs.length; i++) {
      if (inputs[i].checked === true) {
        votes.push(inputs[i].name);
      }
    }

    const json_votes = JSON.stringify([username, votes]);

    const voteResponse = await fetch('/vote', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: json_votes
    });

    const result = await voteResponse.json();
    console.log(result);

  } catch (error) {
    console.error('Error:', error);
  }
}


function delete_votes() {
  fetch('/delete', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

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

function change_vote_unique() {
  fetch('/change_vote_unique', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
}

function change_vote_multiple() {
  fetch('/change_vote_multiple', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
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