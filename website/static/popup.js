let openPopups = document.querySelectorAll(".open-popup");
let popupContents = document.querySelectorAll(".popup-content");
let closePopups = document.querySelectorAll(".close-popup");
let blurBg = document.querySelector(".blur-bg");

// Add popup event for context items
openPopups.forEach(function (openPopup) {
    addEventOpenPopup(openPopup, "click")
});

// Add popup event for document item viewers
document.querySelectorAll(".document-item-viewer").forEach(function (openPopup) {
    addEventOpenPopup(openPopup, "dblclick")
});

// Close popup when click X, click background or press Esc
blurBg.addEventListener("click", closePopupFunction);
closePopups.forEach(function (closePopup) {
    closePopup.addEventListener("click", closePopupFunction);
});
popupContents.forEach(function (popupContent) {
    document.addEventListener("keydown", function (event) {
        if (
            event.key === "Escape" &&
            !popupContent.classList.contains("hidden-popup")
        ) {
            closePopupFunction();
        }
    });
});

// Close popup when certain buttons are clicked
function cancelPopup() {
    closePopupFunction();
}

function addEventOpenPopup(element, type) {
    element.addEventListener(type, function () {
        let documentId = element.getAttribute("document-id");
        let documentTitle = element.getAttribute("document-title");
        let popupId = element.getAttribute("popup-id");

        // Connect popup to menu-action
        let popup = document.getElementById(popupId);

        popup.setAttribute("document-id", documentId);
        popup.setAttribute("document-title", documentTitle);
        popup.querySelector("#document-title").textContent = documentTitle;

        // Handle popup by AJAX
        if (popupId == "detail-popup")
        {
            $.ajax({
                type: 'GET',
                url: `/files/doc/detail/${documentId}`,
                success: function (response) {
                    console.log(response);

                    var imgElement = $('<img>').attr('src', '/buffer/' + response.storage_path);
                    $('#document-image').empty().append(imgElement);

                    // Populate information in the metadata panel
                    $('#createdate-metadata').text(response.create_date);
                    $('#doctype-metadata').text(response.doctype);
                },
                error: function (error) {
                    console.error('Unable to see document detail', error);
                }
            });
        }
        // Handle popup by JS only
        else
        {
            switch (popupId)
            {
                case "create-subfolder-popup":
                    popup.querySelector("#popup-form").action = "/files/folder/create/" + documentId;
                    break;
                case "rename-popup":
                    popup.querySelector("#popup-form").action = "/files/doc/update/" + documentId;
                    break;
                case "delete-folder-popup":
                    popup.querySelector("#popup-form").action = "/files/folder/delete/" + documentId;
                    break;
                case "upload-popup":
                    popup.querySelector("#popup-form").action = "/files/doc/upload/" + documentId;
                    break;
                case "delete-document-popup":
                    popup.querySelector("#popup-form").action = "/files/doc/delete/" + documentId;
                    break;
                case "reindex-popup":
                    popup.querySelector("#popup-form").action = "/index/doc/" + documentId;
                    break;
            }
        }

        popup.classList.remove("hidden-popup");
        blurBg.classList.remove("hidden-blur");
    });
}

function closePopupFunction() {
    popupContents.forEach(function (popupContent) {
        if (!popupContent.classList.contains("hidden-popup"))
            popupContent.classList.add("hidden-popup");
    });
    blurBg.classList.add("hidden-blur");
};