const folderContextMenu = document.querySelector("#rightclick-folder");
const documentContextMenu = document.querySelector("#rightclick-document");

let browserItems = document.querySelectorAll(".browser-item");
let folderItemViewers = document.querySelectorAll(".folder-item-viewer")
let documentItemViewers = document.querySelectorAll(".document-item-viewer");

browserItems.forEach(function (browserItem) {
    browserItem.addEventListener("contextmenu", e => {
        rightClickEvent(e, folderContextMenu)
    })
})

folderItemViewers.forEach(function (folderItemViewer) {
    folderItemViewer.addEventListener("contextmenu", e => {
        rightClickEvent(e, folderContextMenu)
    })
})

documentItemViewers.forEach(function (documentItemViewer) {
    documentItemViewer.addEventListener("contextmenu", e => {
        rightClickEvent(e, documentContextMenu)
    })
})

document.addEventListener("click", () => folderContextMenu.style.visibility = "hidden");
document.addEventListener("click", () => documentContextMenu.style.visibility = "hidden");

function rightClickEvent (event, contextMenu)
{
    event.preventDefault();
    
    let x = event.clientX, y = event.clientY;
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
        rightclickItem.setAttribute("document-id", event.currentTarget.getAttribute("document-id"));
        rightclickItem.setAttribute("document-title", event.currentTarget.getAttribute("document-title"));
    });
}