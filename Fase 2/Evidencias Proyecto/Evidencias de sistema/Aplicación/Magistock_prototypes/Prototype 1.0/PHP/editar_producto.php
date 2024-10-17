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
    $id = $_POST['id'];
    $nombre = $_POST['nombre'];
    $cantidad = $_POST['cantidad'];

    $sql = "UPDATE productos SET nombre='$nombre', stock='$cantidad' WHERE id='$id'";

    if ($conn->query($sql) === TRUE) {
        echo "Producto actualizado exitosamente.";
    } else {
        echo "Error: " . $sql . "<br>" . $conn->error;
    }
}

$conn->close();
?>
