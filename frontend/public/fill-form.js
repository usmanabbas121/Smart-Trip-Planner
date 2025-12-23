// Sample data to fill the ELD Trip Planner form
// Run this in the browser console (F12 -> Console tab) after the page loads

const sampleData = {
  // Required fields
  current_location: "Chicago, IL",
  pickup_location: "Los Angeles, CA",
  dropoff_location: "New York, NY",
  current_cycle_used: 15.5,
  
  // Optional Carrier Information
  carrier_name: "ABC Trucking Company",
  main_office_address: "123 Main St, Chicago, IL 60601",
  home_terminal_address: "456 Terminal Blvd, Chicago, IL 60601",
  driver_name: "John Smith",
  co_driver_name: "Jane Doe",
  
  // Optional Vehicle Information
  truck_tractor: "TRK-12345",
  trailer: "TRL-67890",
  
  // Optional Shipping Information
  dvl_manifest_no: "DVL-2024-001234",
  shipper_commodity: "General Freight - Electronics"
};

// Function to fill the form
function fillForm() {
  // Get all input fields
  const inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
  
  inputs.forEach(input => {
    const name = input.getAttribute('name');
    if (name && sampleData[name] !== undefined) {
      // Set the value
      input.value = sampleData[name];
      
      // Trigger change event to update React state
      const event = new Event('input', { bubbles: true });
      input.dispatchEvent(event);
      
      // Also trigger change event
      const changeEvent = new Event('change', { bubbles: true });
      input.dispatchEvent(changeEvent);
      
      console.log(`Filled ${name}: ${sampleData[name]}`);
    }
  });
  
  console.log('Form filled! Click "Calculate Trip" to submit.');
}

// Auto-fill when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', fillForm);
} else {
  fillForm();
}

// Also export the function for manual use
window.fillELDForm = fillForm;


