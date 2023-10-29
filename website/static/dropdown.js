$(document).ready(function () {
    var keytypeDropdowns = document.querySelectorAll('.keytypes-dropdown');

    $.ajax({
        type: "GET",
        url: "/keytypes/all",
        success: function (response) {
            keytypeDropdowns.forEach(dropdown => {
                // Clear existing options
                dropdown.innerHTML = "";

                response.forEach(option => {
                    var optionElement = document.createElement('option');
                    optionElement.value = option.value;
                    optionElement.textContent = option.text;
                    dropdown.appendChild(optionElement);
                });
            })
        },
        error: function (error) {
            console.log("Error fetching options:", error);
        }
    });
});