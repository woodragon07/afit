function togglePassword() {
    var passwordInput = document.getElementById("password");
    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
}

function showSuccessMessage() {
    var message = document.getElementById("success-message");
    message.style.display = "block";
    setTimeout(function () {
        message.style.display = "none";
    }, 2000);
}