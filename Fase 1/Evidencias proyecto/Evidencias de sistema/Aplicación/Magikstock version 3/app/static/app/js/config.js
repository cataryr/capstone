// Función para mostrar el formulario de edición
function mostrarFormularioEditar(formId, botonId) {
    document.getElementById(formId).style.display = "block";
    document.getElementById(botonId).style.display = "none";
}

// Función para ocultar el formulario de edición y restaurar el botón de editar
function ocultarFormularioEditar(formId, botonId) {
    document.getElementById(formId).style.display = "none";
    document.getElementById(botonId).style.display = "block";
}

// Asignar eventos a los botones de editar
document.getElementById("edit-nombre-button").onclick = function() {
    mostrarFormularioEditar("edit-nombre-form-container", "edit-nombre-button");
};

document.getElementById("edit-apellidos-button").onclick = function() {
    mostrarFormularioEditar("edit-apellidos-form-container", "edit-apellidos-button");
};

document.getElementById("edit-correo-button").onclick = function() {
    mostrarFormularioEditar("edit-correo-form-container", "edit-correo-button");
};

document.getElementById("edit-numero-button").onclick = function() {
    mostrarFormularioEditar("edit-numero-form-container", "edit-numero-button");
};

// Asignar eventos a los botones de cancelar
var cancelButtons = document.getElementsByClassName("cancel-button");
for (var i = 0; i < cancelButtons.length; i++) {
    cancelButtons[i].onclick = function() {
        var formId = this.getAttribute("data-form");
        var botonId = formId.replace("form-container", "button");
        ocultarFormularioEditar(formId, botonId);
    };
}

// Validaciones de formulario antes de enviar
document.querySelector('form').addEventListener('submit', function(event) {
    var nombre = document.getElementById('nombre') ? document.getElementById('nombre').value : '';
    var apellidos = document.getElementById('apellidos') ? document.getElementById('apellidos').value : '';
    var numero = document.getElementById('numero') ? document.getElementById('numero').value : '';

    // Validación de solo letras en nombre y apellidos
    var letraRegex = /^[A-Za-z\s]+$/;
    if (nombre && !letraRegex.test(nombre)) {
        alert('El nombre solo puede contener letras y espacios.');
        event.preventDefault();
    }
    if (apellidos && !letraRegex.test(apellidos)) {
        alert('Los apellidos solo pueden contener letras y espacios.');
        event.preventDefault();
    }

    // Validación de solo números en el número de contacto
    var numeroRegex = /^[0-9]+$/;
    if (numero && !numeroRegex.test(numero)) {
        alert('El número de contacto solo puede contener dígitos.');
        event.preventDefault();
    }
});
