url = "localhost:8080/vote"

function vote() {
    username = prompt("Qual seu usário?")
    let votes = new Array()
    var inputs = document.querySelectorAll("input[type='checkbox']");
    for(var i = 0; i < inputs.length; i++) {
        if(inputs[i].checked === true) {
            votes.push(inputs[i].name)

        }
    }
    console.log(votes)
    json_votes = JSON.stringify([username, votes])
    console.log(json_votes)
    fetch('https://kinipk.pythonanywhere/vote', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: json_votes
      })
      .then(response => response.json())
      .then(data => console.log(data))
      .catch(error => console.error('Error:', error));
      
}
