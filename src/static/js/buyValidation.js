document.addEventListener('DOMContentLoaded', function() {
    var buyForm = document.getElementById('buyForm');
    var sharesInput = document.getElementById('shares');
    var sharesError = document.getElementById('sharesError');

    buyForm.addEventListener('submit', function(event) {
        var sharesValue = sharesInput.value;

        if (!isValidShares(sharesValue)) {
            sharesError.innerText = "Please enter a positive integer for shares.";
            event.preventDefault(); // Prevent the form from being submitted
        } else {
            sharesError.innerText = ""; // Clear the error message if shares are valid
        }
    });

    function isValidShares(value) {
        var numericValue = parseInt(value, 10);

        // Check if it's a valid positive integer (greater than 0)
        return !isNaN(numericValue) && numericValue > 0;
    }
});
