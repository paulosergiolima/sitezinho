// Shared utility functions used across multiple JS modules

/**
 * Clear all checkboxes on the page
 * Used to fix mobile browser caching issues
 */
export function clearAllCheckboxes() {
  const checkboxes = document.querySelectorAll("input[type='checkbox']");
  checkboxes.forEach(checkbox => {
    checkbox.checked = false;
    // Force trigger change event to update any UI that depends on checkbox state
    checkbox.dispatchEvent(new Event('change', { bubbles: true }));
  });
  console.log('All checkboxes cleared');
}

/**
 * Initialize page state - clear checkboxes and verify they're cleared
 * Call this on DOMContentLoaded to ensure clean state
 */
export function initializePage() {
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
}