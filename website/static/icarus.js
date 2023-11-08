$(document).ready(function () {
    $(".icarus-gen").submit(function (event) {
        event.preventDefault();

        var icarus_app = $(this).attr('icarus-app');
        var formData = new FormData();

        // Append form fields manually
        var imageInput = $('#image-input');
        if (imageInput && imageInput.length > 0 && imageInput[0].files.length > 0) {
            formData.append('image', imageInput[0].files[0]);
        }
        var textInput = $('#text-input');
        if (textInput){
            formData.append('text', textInput.val())
        }

        $.ajax({
            type: "POST",
            url: `/icarus/${icarus_app}/generate`,
            data: formData,
            processData: false,
            contentType: false,
            beforeSend: function () {$("#loading-spinner").show();},
            success: function (data) {
                $('#loading-spinner').hide();
                $("#gen-results").html(data);
            },
            error: function (error) {
                $('#loading-spinner').hide();
                console.log("Error:", error);
            }
        });

        
    });
})