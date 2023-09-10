const contextMenu = document.querySelector(".rightclick-wrapper");

let openRightclickMenus = document.querySelectorAll(".open-rightclick-menu");

openRightclickMenus.forEach(function (openRightclickMenu) {
    openRightclickMenu.addEventListener("contextmenu", e => {
        e.preventDefault();
    
        let x = e.clientX, y = e.clientY;
        windowWidth = window.innerWidth;
        windowHeight = window.innerHeight;
        cmWdith = contextMenu.offsetWidth;
        cmHeighth = contextMenu.offsetHeight;
    
        x = x > windowWidth - cmWdith ? windowWidth - cmWdith : x;
        y = y > windowHeight - cmHeighth ? windowHeight - cmHeighth : y;
    
        contextMenu.style.left = `${x}px`;
        contextMenu.style.top = `${y}px`;
        contextMenu.style.visibility = "visible";

        // Set attributes for menu items
        rightclickItems = document.querySelectorAll(".rightclick-item");
        rightclickItems.forEach(function (rightclickItem) {
            rightclickItem.setAttribute("document-id", e.target.getAttribute("document-id"));
            rightclickItem.setAttribute("document-title", e.target.getAttribute("document-title"));
        });
    });
})

document.addEventListener("click", () => contextMenu.style.visibility = "hidden");