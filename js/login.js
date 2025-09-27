window.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const adminLogin = urlParams.get('admin_login');

    // Only default to student view if admin_login is not true
    if (adminLogin !== 'true') {
        document.querySelector(".student-container").classList.remove("hidden");
        document.querySelector(".admin-container").classList.add("hidden");
        document.querySelector(".admin-toggle").classList.remove("hidden");
        document.querySelector(".student-toggle").classList.add("hidden");
    }
});

document.getElementById("admin-btn").addEventListener("click", function() {
    document.querySelector(".student-container").classList.add("hidden");
    document.querySelector(".admin-container").classList.remove("hidden");
    document.querySelector(".admin-toggle").classList.add("hidden");
    document.querySelector(".student-toggle").classList.remove("hidden");
});

document.getElementById("student-btn").addEventListener("click", function() {
    document.querySelector(".student-container").classList.remove("hidden");
    document.querySelector(".admin-container").classList.add("hidden");
    document.querySelector(".admin-toggle").classList.remove("hidden");
    document.querySelector(".student-toggle").classList.add("hidden");
});

function toggleForm(type) {
    const loginForm = document.getElementById(`${type}-login`);
    const signupForm = document.getElementById(`${type}-signup`);
    loginForm.classList.toggle('hidden');
    signupForm.classList.toggle('hidden');
}


function togglePasswordVisibility(inputId) {
    let passwordInput = document.getElementById(inputId);
    let icon = passwordInput.nextElementSibling;

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
        icon.classList.remove("fa-eye-slash");
        icon.classList.add("fa-eye");
    } else {
        passwordInput.type = "password";
        icon.classList.remove("fa-eye");
        icon.classList.add("fa-eye-slash");
    }
}
