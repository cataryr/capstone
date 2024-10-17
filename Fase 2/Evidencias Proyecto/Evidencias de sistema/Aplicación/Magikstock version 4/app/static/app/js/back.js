function toggleDropdown(event) {
    event.preventDefault(); // Evita que el enlace recargue la página
    const dropdown = document.getElementById('dropdownContent');

    // Cambia el estado de visibilidad del dropdown
    dropdown.classList.toggle('show'); // Alterna la clase 'show'
}

function toggleDropdownIcon(event) {
    event.preventDefault(); // Evita que el enlace recargue la página
    const dropdown = document.getElementById('dropdownContentIcon');

    // Cambia el estado de visibilidad del dropdown
    dropdown.classList.toggle('show'); // Alterna la clase 'show'
}

// Cierra el dropdown si el usuario hace clic fuera de él
window.onclick = function(event) {
    const dropdown = document.getElementById('dropdownContent');
    if (!event.target.matches('#gestionStock') && dropdown.classList.contains('show')) {
        dropdown.classList.remove('show'); // Elimina la clase 'show' para ocultar el dropdown
    }
}

window.onresize = function() {
    const dropdownIcon = document.getElementById('dropdownContentIcon');
    const anotherDropdown = document.getElementById('dropdownContent'); // Suponiendo que tienes otro dropdown

    // Cerrar el dropdown de iconos si el ancho es mayor a 800px
    if (window.innerWidth > 800 && dropdownIcon.classList.contains('show')) {
        dropdownIcon.classList.remove('show');
    }

    // Cerrar otro dropdown si el ancho es mayor a 1000px (por ejemplo)
    if (window.innerWidth > 1000 && anotherDropdown.classList.contains('show')) {
        anotherDropdown.classList.remove('show');
    }
};