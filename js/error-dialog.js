// Error Dialog Functions
function showErrorDialog(message) {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'error-dialog-overlay';
    
    // Create dialog box
    const dialog = document.createElement('div');
    dialog.className = 'error-dialog';
    
    // Create header
    const header = document.createElement('div');
    header.className = 'error-dialog-header';
    
    const title = document.createElement('div');
    title.className = 'error-dialog-title';
    title.textContent = 'cec';

    
    const closeBtn = document.createElement('div');
    closeBtn.className = 'error-dialog-close';
    closeBtn.innerHTML = '&times;';
    closeBtn.onclick = () => document.body.removeChild(overlay);
    
    header.appendChild(title);
    header.appendChild(closeBtn);
    
    // Create body
    const body = document.createElement('div');
    body.className = 'error-dialog-body';
    
    const icon = document.createElement('div');
    icon.className = 'error-icon';
    icon.innerHTML = '<span class="icon" style="color: white; font-size: 24px; font-weight: bold;">X</span>';
    


    
    const errorMsg = document.createElement('div');
    errorMsg.className = 'error-message';
    errorMsg.textContent = message;
    
    body.appendChild(icon);
    body.appendChild(errorMsg);
    
    // Create footer
    const footer = document.createElement('div');
    footer.className = 'error-dialog-footer';
    
    const okBtn = document.createElement('button');
    okBtn.className = 'ok-button';
    okBtn.textContent = 'OK';
    okBtn.onclick = () => document.body.removeChild(overlay);
    
    footer.appendChild(okBtn);
    
    // Assemble the dialog
    dialog.appendChild(header);
    dialog.appendChild(body);
    dialog.appendChild(footer);
    
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
}

// Function to check for flash messages and convert them to error dialogs
function handleFlashMessages() {
    // Look for flash message elements - search all error categories
    const errorCategories = ['error', 'login_error', 'signup_error', 'admin_login_error', 'admin_signup_error'];
    
    for (const category of errorCategories) {
        const flashMessages = document.querySelectorAll(`.flash-message.${category}`);
        if (flashMessages.length > 0) {
            // Get the first error message
            const message = flashMessages[0].textContent.trim();
            // Show it in our custom dialog
            showErrorDialog(message);
            // Hide the original flash message
            flashMessages.forEach(el => el.style.display = 'none');
            break; // Only show the first error message found
        }
    }
}

// Run when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initial check for flash messages
    handleFlashMessages();
    
    // Override form submissions to show our custom error dialog
    const studentLoginForm = document.querySelector('#student-login form');
    const studentSignupForm = document.querySelector('#student-signup form');
    const adminLoginForm = document.querySelector('#admin-login form');
    const adminSignupForm = document.querySelector('#admin-signup form');
    
    // Add custom validation to these forms
    if (studentLoginForm) {
        studentLoginForm.addEventListener('submit', function(e) {
            // Client-side validation could be added here if needed
            // For now, we'll let server validation happen
        });
    }
    
    if (studentSignupForm) {
        studentSignupForm.addEventListener('submit', function(e) {
            // Client-side validation could be added here if needed
            // For now, we'll let server validation happen
        });
    }
    
    if (adminLoginForm) {
        adminLoginForm.addEventListener('submit', function(e) {
            // Client-side validation could be added here if needed
            // For now, we'll let server validation happen
        });
    }
    
    if (adminSignupForm) {
        adminSignupForm.addEventListener('submit', function(e) {
            // Client-side validation could be added here if needed
            // For now, we'll let server validation happen
        });
    }
});