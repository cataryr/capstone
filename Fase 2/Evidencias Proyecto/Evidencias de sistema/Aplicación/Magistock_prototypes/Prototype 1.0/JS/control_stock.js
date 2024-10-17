function addNewProduct() {
    const name = document.getElementById('productName').value;
    const quantity = document.getElementById('productQuantity').value;

    if (name && quantity > 0) {
        console.log("Preparando para enviar datos:"); // Punto de depuración
        console.log(`Nombre: ${name}, Cantidad: ${quantity}`);

        const xhr = new XMLHttpRequest();
        xhr.open("POST", "PHP/agregar_producto.php", true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log("Respuesta del servidor:", xhr.responseText); // Mostrar respuesta del servidor
                alert(xhr.responseText);
                location.reload(); // Recargar la página para mostrar el nuevo producto
            } else if (xhr.readyState === 4) {
                console.log("Error al comunicarse con el servidor.");
            }
        };
        xhr.send("nombre=" + encodeURIComponent(name) + "&cantidad=" + encodeURIComponent(quantity));
    } else {
        alert("Por favor, ingresa un nombre válido y una cantidad mayor a cero.");
    }
}



function addStock(productId) {
    // Solicitar cantidad a añadir
    const amount = prompt("¿Cuántas unidades deseas añadir?", "1");
    if (amount && amount > 0) {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "PHP/incrementar_stock.php", true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(xhr.responseText); // Verificar la respuesta del servidor
                location.reload(); // Recargar la página para mostrar el nuevo stock
            }
        };
        xhr.send("id=" + encodeURIComponent(productId) + "&cantidad=" + encodeURIComponent(amount));
    } else {
        alert("Por favor, ingresa una cantidad válida.");
    }
}


function reduceStock(productId) {
    // Solicitar cantidad a reducir
    const amount = prompt("¿Cuántas unidades deseas reducir?", "1");
    if (amount && amount > 0) {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "PHP/reducir_stock.php", true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(xhr.responseText); // Verificar la respuesta del servidor
                location.reload(); // Recargar la página para mostrar el nuevo stock
            }
        };
        xhr.send("id=" + encodeURIComponent(productId) + "&cantidad=" + encodeURIComponent(amount));
    } else {
        alert("Por favor, ingresa una cantidad válida.");
    }
}


// Función para editar un producto
function editProduct(productId, currentName) {
    const newName = prompt("Nuevo nombre del producto:", currentName);
    const newQuantity = prompt("Nueva cantidad del producto:");

    if (newName && newQuantity >= 0) {
        // Enviar datos a PHP mediante AJAX
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "PHP/editar_producto.php", true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(xhr.responseText);
                location.reload(); // Recargar la página para mostrar los cambios
            }
        };
        xhr.send("id=" + productId + "&nombre=" + newName + "&cantidad=" + newQuantity);
    } else {
        alert("Por favor, ingresa un nombre y una cantidad válidos.");
    }
}

// Función para guardar los cambios del producto editado
function saveEdit() {
    const newName = document.getElementById('editProductName').value;
    const newQuantity = document.getElementById('editProductQuantity').value;

    if (newName && newQuantity >= 0) {
        // Lógica para guardar los cambios en la base de datos
        console.log(`Guardar cambios: Nuevo nombre - ${newName}, Nueva cantidad - ${newQuantity}`);
        closeModal();
    } else {
        alert("Por favor, ingresa un nombre válido y una cantidad no negativa.");
    }
}

// Función para eliminar un producto
function deleteProduct(productId) {
    if (confirm("¿Estás seguro de que deseas eliminar este producto?")) {
        // Enviar solicitud a PHP mediante AJAX
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "PHP/eliminar_producto.php", true);
        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4 && xhr.status === 200) {
                console.log(xhr.responseText);
                location.reload(); // Recargar la página para mostrar los cambios
            }
        };
        xhr.send("id=" + productId);
    }
}

// Función para cerrar el modal de edición
function closeModal() {
    document.getElementById('editModal').style.display = 'none';
}



// Las demás funciones se mantienen iguales
