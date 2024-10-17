$(document).ready(function() {
    $('.update-quantity').on('click', function() {
        var action = $(this).data('action');
        var productId = $(this).data('id');
        var quantityElement = $('#cantidad-' + productId);

        $.ajax({
            url: '/update-product-quantity/',  // Asegúrate de que la URL sea correcta
            type: 'POST',
            data: {
                'product_id': productId,
                'action': action,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val() // Obtener el token CSRF del formulario
            },
            success: function(response) {
                if (response.success) {
                    // Actualizamos la cantidad en la interfaz
                    quantityElement.text(response.new_quantity);

                    // Verificamos si la cantidad es inferior a 5 y cambiamos el color
                    if (response.new_quantity < 5) {
                        quantityElement.css('color', 'red');
                        alert('Atención: la cantidad del producto está por debajo de 5.');
                    } else {
                        quantityElement.css('color', 'black');
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
