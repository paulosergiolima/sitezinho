// Global variables for vote configuration (set by template)
let single_vote = false;



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

// Initialize page and modal event listeners when page loads

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

