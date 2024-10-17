<?php
// Conexión a la base de datos MySQL
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "login_test_db";

$conn = new mysqli($servername, $username, $password, $dbname);

if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nombre = $_POST['nombre'];
    $cantidad = $_POST['cantidad'];

    // Verificar si los datos están siendo recibidos correctamente
    if (empty($nombre) || empty($cantidad)) {
        echo "Faltan datos.";
        exit;
    }

    // SQL para insertar el producto en la base de datos
    $sql = "INSERT INTO productos (nombre, stock) VALUES ('$nombre', '$cantidad')";

    if ($conn->query($sql) === TRUE) {
        echo "Producto agregado exitosamente.";
    } else {
        echo "Error al insertar el producto: " . $conn->error;
    }
} else {
    echo "No se recibieron datos POST.";
}

$conn->close();
?>
