$(document).ready(function () {
    // AJAX request for tag
    $("#tag-btn").click(function (event) {
        event.preventDefault();

        var popupContent = $(this).closest(".popup-content");
        var documentId = popupContent.attr("document-id");

        // Get keyword dropdown value
        var tagDropdown = $(this).siblings("#tag-dropdown");
        var keywordId = tagDropdown.val();
            
        var url = `/keywords/tag?doc=${documentId}&keywords=${keywordId}`
        $.ajax({
            type: "POST",
            url: url,
            success: function () {
                if (popupContent.attr("id")=="detail-popup") {
                    // Refresh keyword panel after tagging keyword
                    populateKeywordPnl(documentId)
                }
            },
            error: function (message) {console.log("Error:", message);}
        });
    })
})