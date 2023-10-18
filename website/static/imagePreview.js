image_input = document.getElementById('image-input')
image_form = document.getElementById('image-form')

// Show preview image upon browse image 
image_input.addEventListener('change', function() {
    var previewImage = document.getElementById('preview-image');

    // Display the selected image
    var file = this.files[0];
    var reader = new FileReader();
    reader.onload = function(e) {
        previewImage.src = e.target.result;
    };
    reader.readAsDataURL(file);
});
