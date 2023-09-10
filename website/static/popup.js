let openPopups = document.querySelectorAll(".open-popup");
let popupContent = document.querySelector(".popup-content");
let closePopup = document.querySelector(".close-popup");
let blurBg = document.querySelector(".blur-bg");

openPopups.forEach(function (openPopup) {
    openPopup.addEventListener("click", function () {
        let documentId = openPopup.getAttribute("document-id");
        let documentTitle = openPopup.getAttribute("document-title");
        let popupId = openPopup.getAttribute("popup-id");

        // Connect popup to menu-action
        let popup = document.getElementById(popupId);
         
        let documentTitleSpan = popup.querySelector("#document-title");
        let popupForm = popup.querySelector("#popup-form");
        documentTitleSpan.textContent = documentTitle;
        popupForm.action = "files/" + documentId;

        popup.classList.remove("hidden-popup");
        blurBg.classList.remove("hidden-blur");
    });
})

let closePopupFunction = function () {
    popupContent.classList.add("hidden-popup")
    blurBg.classList.add("hidden-blur")
}

blurBg.addEventListener("click", closePopupFunction);
closePopup.addEventListener("click", closePopupFunction);

// Close popup when press Esc
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape"
     && !popupContent.classList.contains("hidden")
   ) {
        closePopupFunction();
    }
});