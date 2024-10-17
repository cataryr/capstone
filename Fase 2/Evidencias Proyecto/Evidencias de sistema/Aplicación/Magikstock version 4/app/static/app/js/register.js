document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form') || document.getElementById('edit-form');

    if (form) {
        form.addEventListener('submit', function(event) {
            // Variables para validar
            let firstName = document.getElementById('first_name').value.trim();
            let lastName = document.getElementById('last_name').value.trim();
            let email = document.getElementById('email').value.trim();
            let rut = document.getElementById('rut').value.trim();
            let num = document.getElementById('num').value.trim();

            // Validar que no se dejen campos vacíos
            if (!firstName || !lastName || !email || !rut || !num) {
                alert("No puedes dejar campos vacíos.");
                event.preventDefault();
                return;
            }

            // 1. Validar que el nombre y el apellido no contengan números (solo letras)
            const lettersRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
            if (!lettersRegex.test(firstName) || !lettersRegex.test(lastName)) {
                alert("El nombre y el apellido solo pueden contener letras.");
                event.preventDefault();
                return;
            }

            // 2. Validar que el nombre y el apellido tengan al menos 3 caracteres
            if (firstName.length < 3 || lastName.length < 3) {
                alert("El nombre y el apellido deben tener al menos 3 caracteres.");
                event.preventDefault();
                return;
            }

            // 3. Validar formato del correo electrónico
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert("El correo electrónico no es válido.");
                event.preventDefault();
                return;
            }

            // 4. Validar RUT de Chile
            if (!validarRUT(rut)) {
                alert("El RUT ingresado no es válido.");
                event.preventDefault();
                return;
            }

            // 5. Validar que el número de teléfono solo contenga dígitos y sea válido en Chile
            const chilePhoneRegex = /^([29]\d{8})$/;
            if (!chilePhoneRegex.test(num)) {
                alert("El número de teléfono debe ser de 9 dígitos y empezar con 9 o 2.");
                event.preventDefault();
                return;
            }

            // Validación del nombre de usuario (se aplica en registro y edición)
            let username = document.getElementById('new-username') ? document.getElementById('new-username').value.trim() : null;
            if (username) {
                // 6. Validar que el nombre de usuario contenga al menos una letra y pueda incluir números
                const usernameRegex = /^(?=.*[a-zA-Z])[a-zA-Z0-9]+$/;
                if (!usernameRegex.test(username) || username.length < 3) {
                    alert("El nombre de usuario debe contener al menos una letra y puede incluir números, con un mínimo de 3 caracteres.");
                    event.preventDefault();
                    return;
                }
            }

            // Solo validar la contraseña si se está registrando un nuevo usuario
            if (form.id === 'register-form') {
                let password = document.getElementById('new-password').value.trim();

                // 7. Validar que la contraseña tenga al menos 8 caracteres
                if (password.length < 8) {
                    alert("La contraseña debe tener al menos 8 caracteres.");
                    event.preventDefault();
                    return;
                }
            }
        });
    }

    // Función para validar el RUT en el cliente (JavaScript)
    function validarRUT(rut) {
        // Remover puntos y guiones
        rut = rut.replace(/\./g, '').replace('-', '');
        let cuerpo = rut.slice(0, -1);
        let dv = rut.slice(-1).toUpperCase();

        if (cuerpo.length < 7) {
            return false;
        }

        let suma = 0;
        let multiplo = 2;

        for (let i = 1; i <= cuerpo.length; i++) {
            let index = multiplo * rut.charAt(cuerpo.length - i);
            suma = suma + index;
            multiplo = multiplo < 7 ? multiplo + 1 : 2;
        }

        let dvEsperado = 11 - (suma % 11);
        dvEsperado = dvEsperado == 11 ? '0' : dvEsperado == 10 ? 'K' : dvEsperado.toString();

        return dv === dvEsperado;
    }
});


