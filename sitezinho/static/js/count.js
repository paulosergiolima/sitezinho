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

