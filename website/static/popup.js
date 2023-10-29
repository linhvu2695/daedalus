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
    element.addEventListener(type, function() {
        openPopup(element);
    });
}

function openPopup(element) {
    let popupId = element.getAttribute("popup-id");
    let popup = document.getElementById(popupId);

    // Document popup
    if (element.hasAttribute("document-id")){
        handleDocumentPopup(element, popup);
    }

    // Query item popup
    else if (element.hasAttribute("item-id")){
        handleQueryItemPopup(element, popup);
    }

    showPopup(popup);
}

// Show popup and blur background
function showPopup(popup) {
    popup.classList.remove("hidden-popup");
    blurBg.classList.remove("hidden-blur");
}

// Handle Document popup
function handleDocumentPopup(element, popup) {
    // Populate popup attributes from element attributes
    let documentId = element.getAttribute("document-id");
    let documentTitle = element.getAttribute("document-title");
    let title = popup.querySelector("#document-title");

    if (documentId && documentTitle && title)
    {
        popup.setAttribute("document-id", documentId);
        popup.setAttribute("document-title", documentTitle);
        title.textContent = documentTitle;
    }

    let popupId = element.getAttribute("popup-id");
    switch (popupId)
    {
        case "detail-popup":
            popup.querySelector("#popup-form").action = "/files/doc/update/" + documentId;
            populateDocumentDetail(documentId);
            break;
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

function populateDocumentDetail(documentId) {
    $.ajax({
        type: 'GET',
        url: `/files/doc/detail/${documentId}`,
        success: function (response) {
            console.log(response);

            var imgElement = $('<img>').attr('src', '/buffer/' + response.storage_path);
            $('#document-image').empty().append(imgElement);

            // Populate information in the metadata panel
            $('#id-metadata').text(response.id);
            $('#createdate-metadata').text(response.create_date);
            $('#doctype-metadata').text(response.doctype);
            $('#description-metadata').val(response.description);
        },
        error: function (error) {
            console.error('Unable to see document detail', error);
        }
    });
}

// Handle Query item popup
function handleQueryItemPopup(element, popup) {
    // Populate popup attributes from element attributes
    let itemId = element.getAttribute("item-id");
    if (itemId)
    {
        popup.setAttribute("item-id", itemId);
    }

    let popupId = element.getAttribute("popup-id");
    var itemType;
    switch (popupId)
    {
        case "keytype-detail-popup":
            itemType = "keytypes";
            break;
        case "keyword-detail-popup":
            itemType = "keywords";
            break;
    }
    
    populateItemDetail(itemId, itemType);
}

function populateItemDetail(itemId, itemType) {
    $.ajax({
        type: 'GET',
        url: `/${itemType.toLowerCase()}/detail/${itemId}`,
        success: function (response) {
            console.log(response);

            // Populate information in the metadata panel
            $("#item-type-metadata").text(itemType.toUpperCase());
            $('#id-metadata').text(response.id);
            $('#name-metadata').text(response.name);
            $('#createdate-metadata').text(response.create_date);
        },
        error: function (error) {
            console.error('Unable to see item detail', error);
        }
    });
}

function deleteItem(itemId, itemType) {
    $.ajax({
        type: 'POST',
        url: `/${itemType.toLowerCase()}/delete/${itemId}`,
        success: function (response) {
            console.log(response);

            var deleteMessage = $("#delete-message p");
            deleteMessage.text(response["delete_message"]);
            if (!response["success"])
            {
                deleteMessage.css("color", "red");
            }

            // clear search results
            $("#search-results").html("");
        },
        error: function (error) {
            console.error('Unable to see item detail', error);
        }
    });
    
    closePopupFunction();
}

function closePopupFunction() {
    popupContents.forEach(function (popupContent) {
        if (!popupContent.classList.contains("hidden-popup"))
            popupContent.classList.add("hidden-popup");
    });
    blurBg.classList.add("hidden-blur");
};

function toggleEditMode() {
    var descriptionMetadata = document.getElementById('description-metadata');
    var saveButton = document.getElementById('save-btn');

    if (saveButton.hasAttribute('disabled')) {
        // Enable edit mode
        saveButton.removeAttribute('disabled');
        descriptionMetadata.removeAttribute('readonly');        
        descriptionMetadata.style.backgroundColor = '';
    } else {
        // Disable edit mode
        descriptionMetadata.setAttribute('readonly', 'readonly');
        saveButton.setAttribute('disabled', 'disabled');
        descriptionMetadata.style.backgroundColor = '#d3d3d3';
    }
}