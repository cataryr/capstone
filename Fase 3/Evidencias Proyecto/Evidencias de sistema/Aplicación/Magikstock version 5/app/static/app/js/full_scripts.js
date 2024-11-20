// BASE --------------------------------------------------------------
// -------------------------------------------------------------------
// -------------------------------------------------------------------

// Visualizar menú desplegable en Gestión de stock.
function toggleDropdown(event) {
    event.preventDefault();
    const dropdown = document.getElementById('dropdownContent');
    dropdown.classList.toggle('show');
}

// Visualizar menú desplegable en Gestión de stock (Android).
function toggleDropdownIcon(event) {
    event.preventDefault();
    const dropdown = document.getElementById('dropdownContentIcon');
    dropdown.classList.toggle('show'); 
}

// Cierra el menú desplegable si el usuario hace clic fuera de él.
window.onclick = function(event) {
    const dropdown = document.getElementById('dropdownContent');
    if (!event.target.matches('#gestionStock') && dropdown.classList.contains('show')) {
        dropdown.classList.remove('show');
    }
}

// Cierra los menús en caso de cambios de tamaño en la pantalla.
window.onresize = function() {
    const dropdownIcon = document.getElementById('dropdownContentIcon');
    const anotherDropdown = document.getElementById('dropdownContent');
    if (window.innerWidth > 800 && dropdownIcon.classList.contains('show')) {
        dropdownIcon.classList.remove('show');
    }
    if (window.innerWidth > 1000 && anotherDropdown.classList.contains('show')) {
        anotherDropdown.classList.remove('show');
    }
};

// Desactivar los enlaces de las páginas cuando se esta dentro.
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.nav-link.disabled').forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
        });
    });
});



// HOME --------------------------------------------------------------
// -------------------------------------------------------------------
// -------------------------------------------------------------------

// FILTRO DE FECHAS: Bloquear dias posteriores al presente.
document.addEventListener("DOMContentLoaded", function() {
    const today = new Date().toISOString().split("T")[0];
    document.getElementById("fecha_inicio").setAttribute("max", today);
    document.getElementById("fecha_fin").setAttribute("max", today);
});

// CATEGORIAS --------------------------------------------------------
// -------------------------------------------------------------------
// -------------------------------------------------------------------

// MENSAJES
window.addEventListener('DOMContentLoaded', (event) => {
    setTimeout(function() {
        const alertMessage = document.querySelector('.alert');
        if (alertMessage) {
            alertMessage.classList.add('fade-out');
            setTimeout(function() {
                alertMessage.remove();
            }, 1000); 
        }
    }, 2000);
});


// EMPLEADOS --------------------------------------------------------
// -------------------------------------------------------------------
// -------------------------------------------------------------------

// Validaciones para registrar empleados
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('register-form') || document.getElementById('edit-form');

    if (form) {
        form.addEventListener('submit', function(event) {
            let firstName = document.getElementById('first_name').value.trim();
            let lastName = document.getElementById('last_name').value.trim();
            let email = document.getElementById('email').value.trim();
            let rut = document.getElementById('rut').value.trim();
            let num = document.getElementById('num').value.trim();

            if (!firstName || !lastName || !email || !rut || !num) {
                alert("No puedes dejar campos vacíos.");
                event.preventDefault();
                return;
            }
            
            const lettersRegex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
            if (!lettersRegex.test(firstName) || !lettersRegex.test(lastName)) {
                alert("El nombre y el apellido solo pueden contener letras.");
                event.preventDefault();
                return;
            }

            if (firstName.length < 3 || lastName.length < 3) {
                alert("El nombre y el apellido deben tener al menos 3 caracteres.");
                event.preventDefault();
                return;
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert("El correo electrónico no es válido.");
                event.preventDefault();
                return;
            }

            if (!validarRUT(rut)) {
                alert("El RUT ingresado no es válido.");
                event.preventDefault();
                return;
            }

            const chilePhoneRegex = /^([29]\d{8})$/;
            if (!chilePhoneRegex.test(num)) {
                alert("El número de teléfono debe ser de 9 dígitos y empezar con 9 o 2.");
                event.preventDefault();
                return;
            }

            let username = document.getElementById('new-username') ? document.getElementById('new-username').value.trim() : null;
            if (username) {
                const usernameRegex = /^(?=.*[a-zA-Z])[a-zA-Z0-9]+$/;
                if (!usernameRegex.test(username) || username.length < 3) {
                    alert("El nombre de usuario debe contener al menos una letra y puede incluir números, con un mínimo de 3 caracteres.");
                    event.preventDefault();
                    return;
                }
            }

            if (form.id === 'register-form') {
                let password = document.getElementById('new-password').value.trim();

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