$(document).ready(function() {
    // Verificar la cantidad de stock al cargar la página y aplicar el color correspondiente
    $('.cantidad').each(function() {
        var quantity = parseInt($(this).text());
        if (quantity < 5) {
            $(this).css({'color': 'red', 'font-weight': 'bold'});
        } else if (quantity >= 5 && quantity < 10) {
            $(this).css({'color': '#FF8C00', 'font-weight': 'bold'});
        } else {
            $(this).css({'color': 'green', 'font-weight': 'bold'});
        }
    });

    // Manejar el clic para actualizar la cantidad
    $('.update-quantity').on('click', function() {
        var action = $(this).data('action');
        var productId = $(this).data('id');
        var quantityElement = $('#cantidad-' + productId);

        $.ajax({
            url: '/update-product-quantity/',
            type: 'POST',
            data: {
                'product_id': productId,
                'action': action,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Actualizamos la cantidad en la interfaz
                    quantityElement.text(response.new_quantity);

                    // Verificamos la cantidad y aplicamos el color correspondiente
                    if (response.new_quantity < 5) {
                        quantityElement.css({'color': 'red', 'font-weight': 'bold'});
                        alert('Atención: la cantidad del producto está por debajo de 5.');
                    } else if (response.new_quantity >= 5 && response.new_quantity < 10) {
                        quantityElement.css({'color': '#FF8C00', 'font-weight': 'bold'});
                    } else {
                        quantityElement.css({'color': 'green', 'font-weight': 'bold'});
                    }
                } else {
                    alert(response.error);
                }
            },
            error: function() {
                alert('Ocurrió un error al intentar actualizar la cantidad.');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var alert = document.getElementById('alertMessage');
    if (alert) {
        // Configura el cierre automático de la alerta después de 10 segundos
        setTimeout(function() {
            // Agrega la clase hide para que se realice la transición de desvanecimiento
            alert.classList.add('hide');
            
            // Elimina el mensaje completamente después de la animación (500ms)
            setTimeout(function() {
                alert.remove();
            }, 500); // Tiempo de espera de 500ms, que coincide con la duración de la animación
        }, 3000); // 10000 ms = 10 segundos
    }
});

// BUSCADOR DINAMICO.
document.addEventListener("DOMContentLoaded", function() {
    // Obtén el input de búsqueda
    const searchInput = document.getElementById("searchInput");

    // Obtén todas las filas de la tabla
    const table = document.getElementById("productosTable");
    const rows = table.getElementsByTagName("tr");

    // Función para filtrar las filas de la tabla
    searchInput.addEventListener("keyup", function() {
        const filter = searchInput.value.toLowerCase();
        
        // Itera sobre las filas de la tabla
        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName("td");

            // Si la fila tiene celdas
            if (cells.length > 0) {
                let matchFound = false;

                // Itera sobre las celdas de la fila
                for (let j = 0; j < cells.length; j++) {
                    const cell = cells[j];
                    if (cell.textContent.toLowerCase().includes(filter)) {
                        matchFound = true;
                        break; // Si hay coincidencia, no seguimos buscando en las otras celdas
                    }
                }

                // Muestra o esconde la fila dependiendo si hay coincidencia
                if (matchFound) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            }
        }
    });
});
