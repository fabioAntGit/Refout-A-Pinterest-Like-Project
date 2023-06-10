var button = document.getElementById("myButton");
var element = document.getElementById("myElement");

button.onclick = function() {
    if (element.style.display === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }
};