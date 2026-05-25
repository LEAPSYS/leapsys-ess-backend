frappe.provide("leapsys_ess");

// Simple UI Component to show App Status in Frappe Desk
$(document).on('app_ready', function() {
    console.log("Leapsys ESS Backend UI Component Loaded");
    
    // Add a simple status indicator or UI component to the navbar
    if (frappe.boot.user.name !== "Guest") {
        setTimeout(() => {
            frappe.show_alert({
                message: __('Leapsys ESS Mobile Backend API is Active'),
                indicator: 'green'
            });
        }, 3000);
    }
});
