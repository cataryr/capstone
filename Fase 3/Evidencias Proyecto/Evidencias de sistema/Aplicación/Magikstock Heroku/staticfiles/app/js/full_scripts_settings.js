// Variable para detectar cambios en el formulario
let formChanged = false; 

function toggleField(fieldId, button) {
    const input = document.getElementById(fieldId);
    
    if (input) {
        // Alternar el estado readonly
        input.readOnly = !input.readOnly;

        if (!input.readOnly) {
            input.focus(); // Enfocar el campo para editar

            // Escuchar cambios en el campo
            input.addEventListener('input', function() {
                formChanged = true; 
                enableSaveButton();
            });
        }

        // Cambiar el icono del botón a una imagen usando los data attributes
        const iconEdit = button.dataset.iconEdit;
        const iconCancel = button.dataset.iconCancel;
        button.innerHTML = `<img src="${input.readOnly ? iconEdit : iconCancel}" alt="${input.readOnly ? 'Editar' : 'Cancelar'}" style="width: 20px; height: 20px;">`;

        // Mostrar u ocultar el botón "Guardar Cambios"
        const saveBtn = document.getElementById('save-btn');
        if (!input.readOnly) {
            saveBtn.style.display = 'block';
        } else {
            const allReadOnly = [...document.querySelectorAll('.input-edit')].every(input => input.readOnly);
            saveBtn.style.display = allReadOnly ? 'none' : 'block';
        }
    } else {
        console.error("No se encontró el elemento con id:", fieldId);
    }
}

function enableSaveButton() {
    const saveBtn = document.getElementById('save-btn');
    if (formChanged) {
        saveBtn.style.display = 'block';
    }
}

