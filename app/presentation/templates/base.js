function flash_messages(list) {
    for (var i = 0; i < list.length; i++) {
        var message = list[i];
        bootbox.alert(message);
    }
}

function busy_indication_on() {
    document.getElementsByClassName("busy-indicator")[0].style.display = "block";
}

function busy_indication_off() {
    document.getElementsByClassName("busy-indicator")[0].style.display = "none";
}

//how to set the active item in the navigation menu to a distinct color (active)
window.onload = e => {
    document.querySelector(".navbar-nav").addEventListener("click", e => {
        console.log(e);
        e.target.parentElement.classList.add('active');
    });
};