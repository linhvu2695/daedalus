const folderContextMenu = document.querySelector("#rightclick-folder");
const documentContextMenu = document.querySelector("#rightclick-document");

// TODO: use only 1 context menu (else we have to make sure only 1 context menu is visible at a time)

let browserItems = document.querySelectorAll(".browser-item");
let folderItemViewers = document.querySelectorAll(".folder-item-viewer")
let documentItemViewers = document.querySelectorAll(".document-item-viewer");

browserItems.forEach(function (browserItem) {
    browserItem.addEventListener("contextmenu", e => {
        handleRightClickEvent(e, folderContextMenu)
    })

    addDragDropEvents(browserItem);
})

folderItemViewers.forEach(function (folderItemViewer) {
    folderItemViewer.addEventListener("contextmenu", e => {
        handleRightClickEvent(e, folderContextMenu)
    })

    folderItemViewer.addEventListener("dblclick", e => {
        const documentId = e.currentTarget.getAttribute('document-id');

        if (documentId) {
            const url = `/files/folder/${documentId}`;
            window.location.href = url;
        }
    })
})

documentItemViewers.forEach(function (documentItemViewer) {
    documentItemViewer.addEventListener("contextmenu", e => {
        handleRightClickEvent(e, documentContextMenu)
    })

    documentItemViewer.addEventListener("dragstart", e => {
        e.currentTarget.style.opacity = 0.5;
        e.dataTransfer.setData('document-id', e.currentTarget.getAttribute('document-id'))
    })

    documentItemViewer.addEventListener("dragend", e => {
        e.currentTarget.style.opacity = 1;
    })
})

document.addEventListener("click", () => folderContextMenu.style.visibility = "hidden");
document.addEventListener("click", () => documentContextMenu.style.visibility = "hidden");

// Event hanlders 

function handleRightClickEvent (event, contextMenu)
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

function addDragDropEvents (element) 
{
    element.addEventListener("dragover", e => {
        e.preventDefault();
        element.classList.add("drag-over");
    })

    element.addEventListener("dragleave", () => {
        element.classList.remove("drag-over");
    })

    element.addEventListener("drop", e => {
        e.preventDefault();
        element.classList.remove("drag-over");
        documentId = e.dataTransfer.getData('document-id')
        if (documentId) {
            console.log(`Moving ${documentId} to ${element.getAttribute('document-id')}`)

            $.ajax({
                type: 'POST',
                url: `/files/doc/update/${documentId}`,
                data: { 'mother': element.getAttribute('document-id')},
                success: function (response) {
                    console.log(`Moved ${e.dataTransfer.getData('document-title')} to folder ${element.getAttribute('document-title')}`);
                    if (response.redirect) {
                        window.location.href = response.redirect_url;
                    }
                },
                error: function (error) {
                    console.error('Unable to move document', error);
                }
            });
        }
    })
}

// Seethru
$(document).ready(function () {
    var toggler = $("#seethru-toggle-btn");
    
    toggler.click(function () {
        // Toggle the 'active' class on the toggler UI
        toggler.toggleClass('active');

        var isActive = toggler.hasClass('active');

        // Make an AJAX request to set the session variable
        $.ajax({
            type: 'POST', 
            url: '/seethru', 
            data: { isActive: isActive }, 
            success: function (response) {
                console.log('Session seethru set successfully');
                if (response.redirect) {
                    window.location.href = response.redirect_url;
                }
            },
            error: function (error) {
                console.error('Error setting session seethru:', error);
            }
        });
    });
});

