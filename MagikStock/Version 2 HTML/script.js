// EFECTO CONTENEDOR DE INFORMACIÓN

document.getElementById('more-info').addEventListener('click', function(event) {
    event.preventDefault(); // Previene el comportamiento por defecto del enlace
    var infoContent = document.getElementById('info-content');
    var moreInfoLink = document.getElementById('more-info');

    if (infoContent.classList.contains('show')) {
        // Cierra el contenido con animación
        infoContent.style.maxHeight = infoContent.scrollHeight + "px"; // Expande el contenido para ver el tamaño completo
        // Usamos `setTimeout` para permitir que la transición sea visible
        setTimeout(function() {
            infoContent.classList.remove('show');
            infoContent.style.maxHeight = '0'; // Colapsa el contenido
            moreInfoLink.textContent = 'más información'; // Cambia el texto
        }, 10); // Este valor pequeño permite que la animación sea visible antes de hacer el colapso
    } else {
        // Abre el contenido con animación
        infoContent.classList.add('show');
        // Ajusta max-height para mostrar el contenido
        infoContent.style.maxHeight = infoContent.scrollHeight + 'px';
        moreInfoLink.textContent = 'Cerrar'; // Cambia el texto
    }
});

// MOVIMIENTO ENTRE PAGINAS [Se puede eliminar más adelante, solo estético]

document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Previene el envío del formulario

    // Muestra la pantalla de carga
    var loadingScreen = document.getElementById('loading-screen');
    loadingScreen.classList.add('show');

    // Simula una espera de 2 segundos antes de redirigir
    setTimeout(function() {
        window.location.href = 'home.html'; // Redirige a home.html
    }, 2000); // Ajusta el tiempo de espera según sea necesario
});






