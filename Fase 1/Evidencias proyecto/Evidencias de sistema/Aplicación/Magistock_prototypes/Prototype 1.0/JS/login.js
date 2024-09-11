document.getElementById('loginForm').addEventListener('submit', function(event) {
    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;

    if (username.trim() === "" || password.trim() === "") {
        alert("Por favor, rellena todos los campos.");
        event.preventDefault();
    }
});
