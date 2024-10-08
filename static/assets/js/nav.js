const navsection = document.getElementById('navsection');

function toggleNav() {
    navsection.classList.toggle('hidden');
}

window.onclick = function(event) {
    if (!event.target.matches('.navsec')) {
        navsection.classList.add('hidden');
    }
}