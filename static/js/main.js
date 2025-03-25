url = "localhost:8080/vote"
single_vote = false
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
    fetch('https://kinipk.pythonanywhere.com/vote', {
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