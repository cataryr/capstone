<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "login_test_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $user = $_POST['username'];
    $pass = $_POST['password'];

    $user = $conn->real_escape_string($user);

    $sql = "SELECT * FROM usuarios WHERE username = '$user'";
    $result = $conn->query($sql);

    if ($result->num_rows > 0) {
        $row = $result->fetch_assoc();
        
        if (password_verify($pass, $row['password'])) {
            echo "<script>
                alert('Sesión iniciada');
                window.location.href = '../control_stock.php';
              </script>";
        } else {
            echo "Contraseña incorrecta.";
        }
    } else {
        echo "Usuario no encontrado.";
    }
    
}

$conn->close();
?>