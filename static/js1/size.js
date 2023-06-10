var input = document.getElementById('image');
input.addEventListener('change', function() {
    var file = this.files[0];
    if (file.type.match(/image.*/) && file.size <= 1080 * 1080) {
        // The file is an image and its size is less than or equal to 1080 x 1080 pixels
    } else {
        alert('Please select an image file with size less than or equal to 1080 x 1080 pixels.');
        this.value = '';
    }
});