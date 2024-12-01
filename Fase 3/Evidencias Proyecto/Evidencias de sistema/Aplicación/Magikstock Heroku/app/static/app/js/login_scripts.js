document.addEventListener("DOMContentLoaded", function() {
    // Verifica si el parámetro de error está en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const errorParam = urlParams.get('error');

    if (errorParam === '1') {
        // Crear y mostrar el mensaje de error
        const messageBox = document.createElement("div");
        messageBox.className = "error-message";
        messageBox.innerText = "Usuario y/o contraseña incorrectos";

        document.body.appendChild(messageBox);

        // Efecto de entrada (fade-in)
        setTimeout(() => {
            messageBox.classList.add("fade-in");
        }, 100);

        // Eliminar el mensaje con efecto de salida (fade-out) después de 5 segundos
        setTimeout(() => {
            messageBox.classList.remove("fade-in");
            messageBox.classList.add("fade-out");
            setTimeout(() => messageBox.remove(), 1000);
        }, 3000);

        // Vaciar los campos de entrada
        const usernameField = document.querySelector('input[name="username"]');
        const passwordField = document.querySelector('input[name="password"]');
        
        if (usernameField) usernameField.value = "";
        if (passwordField) passwordField.value = "";

        // Elimina el parámetro de error de la URL para evitar que el mensaje reaparezca al recargar
        urlParams.delete('error');
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Elimina el enfoque automático del campo de usuario
    const usernameField = document.querySelector('input[name="username"]');
    if (usernameField) {
        usernameField.setAttribute('autofocus', 'false');
        usernameField.blur();
    }
});