document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');

    // Datos de usuario de ejemplo
    const users = [
        { username: 'admin', password: 'admin123', role: 'administrador' },
        { username: 'empleado', password: 'empleado123', role: 'empleador' }
    ];

    loginForm.addEventListener('submit', function (event) {
        event.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const user = users.find(user => user.username === username && user.password === password);

        if (user) {
            // Guardar los datos del usuario en localStorage o sessionStorage
            sessionStorage.setItem('loggedUser', JSON.stringify(user));

            // Redirigir según el rol del usuario
            if (user.role === 'administrador') {
                window.location.href = 'index.html'; // Página de administrador
            } else if (user.role === 'empleador') {
                window.location.href = 'empleador.html'; // Página de empleador
            }
        } else {
            loginError.textContent = 'Usuario o contraseña incorrectos';
            loginError.style.display = 'block';
        }
    });
});
