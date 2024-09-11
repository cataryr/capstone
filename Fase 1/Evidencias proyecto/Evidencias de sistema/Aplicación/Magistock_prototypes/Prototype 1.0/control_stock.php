<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prototipo Control de Stock</title>
</head>
<body>
    <h2>Prototipo Control de Stock</h2>
    
    <!-- Formulario para agregar productos -->
    <div class="form-container">
        <h3>Agregar Nuevo Producto</h3>
        <input type="text" id="productName" placeholder="Nombre del producto">
        <input type="number" id="productQuantity" placeholder="Cantidad inicial" min="1">
        <button onclick="addNewProduct()">Agregar Producto</button>
    </div>

    <!-- Tabla para el control de stock -->
    <table>
        <thead>
            <tr>
                <th>Producto</th>
                <th>Cantidad</th>
                <th>Acciones</th>
            </tr>
        </thead>
        <tbody id="stockTable">
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

            $sql = "SELECT * FROM productos";
            $result = $conn->query($sql);

            if ($result->num_rows > 0) {
                while($row = $result->fetch_assoc()) {
                    echo "<tr>
                            <td>{$row['nombre']}</td>
                            <td>{$row['stock']}</td>
                            <td>
                                <button onclick=\"addStock({$row['id']})\">+</button>
                                <button onclick=\"reduceStock({$row['id']})\">-</button>
                                <button onclick=\"editProduct({$row['id']}, '{$row['nombre']}')\">Editar</button>
                                <button onclick=\"deleteProduct({$row['id']})\">Eliminar</button>
                            </td>
                          </tr>";
                }
            } else {
                echo "<tr><td colspan='3'>No hay productos en el inventario.</td></tr>";
            }

            $conn->close();
            ?>
        </tbody>
    </table>
    

    <script src="js/control_stock.js"></script>
</body>
</html>


