$(document).ready(function () {
    // AJAX request for search
    $("#search-form").submit(function (event) {
        event.preventDefault();
        
        var url = $(this).attr('url');
        var freetextTerm = $("#freetext-term").val();
        var formData = $(this).serialize();

        $.ajax({
            type: "GET",
            url: url,
            data: formData,
            success: function (data) {
                $("#freetext-term").val(freetextTerm);
                $("#search-results").html(data);
            },
            error: function (error) {
                console.log("Error:", error);
            }
        });
    });

    // AJAX request for create
    $("#create-popup-form").submit(function(event) {
        event.preventDefault();

        var tableName = $(this).attr('table');
        var formData = $(this).serialize();
        var url = "";

        switch (tableName)
        {
            case "keytype":
                url = "/keytypes/create";
                break;
        }

        $.ajax({
            type: "POST",
            url: "/keytypes/create",
            data: formData,
            dataType: "json",
            success: function (response) {
                var createMessage = $("#create-message p");
                createMessage.text(response["create_new_message"]);
                if (!response["success"])
                {
                    createMessage.css("color", "red");
                }
            },
            error: function (error) {
                console.log("Error:", error);
            }
        })
        closePopupFunction()
    })
});