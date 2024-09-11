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

// Datos de prueba
$nombre = "Producto de prueba";
$cantidad = 10;

// SQL para insertar el producto en la base de datos
$sql = "INSERT INTO productos (nombre, stock) VALUES ('$nombre', '$cantidad')";

if ($conn->query($sql) === TRUE) {
    echo "Producto agregado exitosamente.";
} else {
    echo "Error al insertar el producto: " . $conn->error;
}

$conn->close();
?>
