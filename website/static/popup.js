let openPopups = document.querySelectorAll(".open-popup");
let popupContents = document.querySelectorAll(".popup-content");
let closePopups = document.querySelectorAll(".close-popup");
let blurBg = document.querySelector(".blur-bg");

openPopups.forEach(function (openPopup) {
    openPopup.addEventListener("click", function () {
        let documentId = openPopup.getAttribute("document-id");
        let documentTitle = openPopup.getAttribute("document-title");
        let popupId = openPopup.getAttribute("popup-id");

        // Connect popup to menu-action
        let popup = document.getElementById(popupId);

        if (popup != null) {
            popup.setAttribute("document-id", documentId);
            popup.setAttribute("document-title", documentTitle);
            switch (popupId)
            {
                case "create-subfolder-popup":
                    popup.querySelector("#document-title").textContent = documentTitle;
                    popup.querySelector("#popup-form").action = "files/folder/" + documentId;
                    break;
                case "delete-folder-popup":
                    popup.querySelector("#document-title").textContent = documentTitle;
                    popup.querySelector("#popup-form").action = "files/folder/delete/" + documentId;
                    // popup.querySelector("#popup-form").method = "DELETE";
                    break;
            }

            popup.classList.remove("hidden-popup");
        }

        blurBg.classList.remove("hidden-blur");
    });
});

let closePopupFunction = function () {
    popupContents.forEach(function (popupContent) {
        if (!popupContent.classList.contains("hidden-popup"))
            popupContent.classList.add("hidden-popup");
    });
    blurBg.classList.add("hidden-blur");
};

blurBg.addEventListener("click", closePopupFunction);
closePopups.forEach(function (closePopup) {
    closePopup.addEventListener("click", closePopupFunction);
});

// Close popup when press Esc
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

function cancelDelete() {
    closePopupFunction();
}
