$(document).ready(function () {
    var keytypeDropdowns = document.querySelectorAll('.keytypes-dropdown');
    var keywordDropdowns = document.querySelectorAll('.keywords-dropdown');

    if (keytypeDropdowns.length > 0) populateKeytypeDropdowns(keytypeDropdowns);
    if (keywordDropdowns.length > 0) populateKeywordDropdowns(keywordDropdowns);
    
});

function populateKeytypeDropdowns(keytypeDropdowns) {
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
}

function populateKeywordDropdowns(keywordDropdowns) {
    $.ajax({
        type: "GET",
        url: "/keywords/all",
        success: function (response) {
            keywordDropdowns.forEach(dropdown => {
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
}