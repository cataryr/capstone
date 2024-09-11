// EFECTO CONTENEDOR DE INFORMACIÓN
document.getElementById('more-info').addEventListener('click', function(event) {
    event.preventDefault(); // Previene el comportamiento por defecto del enlace
    var infoContent = document.getElementById('info-content');
    var moreInfoLink = document.getElementById('more-info');

    if (infoContent.classList.contains('show')) {
        // Cierra el contenido con animación
        infoContent.style.maxHeight = infoContent.scrollHeight + "px";
        setTimeout(function() {
            infoContent.classList.remove('show');
            infoContent.style.maxHeight = '0';
            moreInfoLink.textContent = 'más información';
        }, 10);
    } else {
        // Abre el contenido con animación
        infoContent.classList.add('show');
        infoContent.style.maxHeight = infoContent.scrollHeight + 'px';
        moreInfoLink.textContent = 'Cerrar';
    }
});

// MUESTRA EL MODAL AL HACER CLIC EN INICIAR SESIÓN
document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Previene el envío del formulario
    var loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
});

// REDIRECCIONA SEGÚN LA OPCIÓN SELECCIONADA
document.getElementById('admin-login').addEventListener('click', function() {
    window.location.href = 'home.html'; // Redirige a home.html
});

document.getElementById('employee-login').addEventListener('click', function() {
    window.location.href = 'home_2.html'; // Redirige a bi.html
});

// CERRAR SESION
document.addEventListener('DOMContentLoaded', function() {
    // Encuentra el formulario de cerrar sesión
    var logoutForm = document.getElementById('logout-form');

    // Añade un evento de envío al formulario
    logoutForm.addEventListener('submit', function(event) {
        // Evita que el formulario se envíe de la manera tradicional
        event.preventDefault();

        // Borra el historial de navegación
        window.location.replace('login.html'); // Usa replace para reemplazar la URL actual en el historial
    });
});







