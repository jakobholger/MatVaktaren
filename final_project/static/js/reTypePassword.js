document.addEventListener('DOMContentLoaded', function () {
    const registrationForm = document.getElementById('registrationForm');
    const passwordInput = document.getElementById('password');
    const retypePasswordInput = document.getElementById('confirmation');
    const passwordError = document.getElementById('passwordError');

    function toggleRetypePassword() {
        if (passwordInput.value.trim() !== '') {
            retypePasswordInput.style.display = 'block';
            retypePasswordInput.required = true;
        } else {
            retypePasswordInput.style.display = 'none';
            retypePasswordInput.required = false;
            retypePasswordInput.value = '';
            passwordError.textContent = ''; // Clear error message when hiding the field
            passwordError.classList.remove('text-danger'); // Remove the text-danger class
        }
    }

    // Initial setup
    toggleRetypePassword();

    passwordInput.addEventListener('input', function () {
        toggleRetypePassword();
        validatePasswordsMatch();
    });

    retypePasswordInput.addEventListener('blur', function () {
        validatePasswordsMatch();
    });

    registrationForm.addEventListener('submit', function (event) {
        if (!validatePasswordsMatch()) {
            event.preventDefault(); // Prevent form submission
        }
    });

    function validatePasswordsMatch() {
        const password = passwordInput.value;
        const retypePassword = retypePasswordInput.value;

        if (retypePassword !== '' && password !== retypePassword) {
            passwordError.textContent = 'Passwords do not match';
            passwordError.classList.add('error-text'); // Add the class for styling
            retypePasswordInput.setCustomValidity("Passwords do not match");
            return false;
        } else {
            passwordError.textContent = '';
            passwordError.classList.remove('error-text'); // Remove the class if no error
            retypePasswordInput.setCustomValidity("");
            return true;
        }
    }
});
