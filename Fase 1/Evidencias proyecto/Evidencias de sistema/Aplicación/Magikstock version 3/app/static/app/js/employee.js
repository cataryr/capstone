// GESTION DE EMPLEADOS

document.addEventListener('DOMContentLoaded', () => {
    const employeeForm = document.getElementById('employee-form_2');
    const employeeTableBody = document.getElementById('employee-table-body_2');
    const submitButton = employeeForm.querySelector('button[type="submit"]'); // Cambiado para seleccionar el botón de submit del formulario

    let editingRow = null;

    employeeForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const name = document.getElementById('employee-name_2').value;
        const role = document.getElementById('employee-role_2').value;
        const description = document.getElementById('employee-description_2').value;

        if (name && role && description) {
            if (editingRow) {
                // Actualiza la fila existente
                editingRow.innerHTML = `
                    <td>${name}</td>
                    <td>${role}</td>
                    <td>${description}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editRow(this)">Editar</button>
                        <button class="btn btn-danger btn-sm" onclick="removeRow(this)">Eliminar</button>
                    </td>
                `;
                editingRow = null;
                submitButton.textContent = 'Agregar Empleado'; // Cambia el texto del botón a 'Agregar Empleado'
            } else {
                // Crea una nueva fila
                const newRow = document.createElement('tr');

                newRow.innerHTML = `
                    <td>${name}</td>
                    <td>${role}</td>
                    <td>${description}</td>
                    <td>
                        <button class="btn btn-warning btn-sm" onclick="editRow(this)">Editar</button>
                        <button class="btn btn-danger btn-sm" onclick="removeRow(this)">Eliminar</button>
                    </td>
                `;

                employeeTableBody.appendChild(newRow);
            }

            employeeForm.reset();
        } else {
            alert('Por favor, completa todos los campos.');
        }
    });

    // Función para eliminar una fila de la tabla
    window.removeRow = function(button) {
        const row = button.closest('tr');
        row.remove();
    }

    // Función para editar una fila de la tabla
    window.editRow = function(button) {
        editingRow = button.closest('tr');

        // Llena el formulario con los datos de la fila
        const cells = editingRow.querySelectorAll('td');
        document.getElementById('employee-name_2').value = cells[0].textContent;
        document.getElementById('employee-role_2').value = cells[1].textContent;
        document.getElementById('employee-description_2').value = cells[2].textContent;

        submitButton.textContent = 'Modificar Empleado'; // Cambia el texto del botón a 'Modificar Empleado'
    }
});

