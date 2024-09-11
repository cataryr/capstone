document.addEventListener('DOMContentLoaded', function () {
    const stockTable = document.getElementById('stock-table').getElementsByTagName('tbody')[0];
    const stockForm = document.getElementById('stockForm');
    const productoInput = document.getElementById('producto');
    const cantidadInput = document.getElementById('cantidad');
    const categoriaSelect = document.getElementById('categoria');
    const proveedorSelect = document.getElementById('proveedor');
    const filtroCategoria = document.getElementById('filtroCategoria');
    const filtroProveedor = document.getElementById('filtroProveedor');
    const aplicarFiltroBtn = document.getElementById('aplicarFiltro');
    const modal = document.getElementById('modal');
    const modalMessage = document.getElementById('modalMessage');
    const closeBtn = document.querySelector('.close-btn');
    const modalImage = document.getElementById('modalImage');

    let stockData = [
        { producto: 'Café', cantidad: 50, categoria: 'Bebidas', proveedor: 'Proveedor A', orangeAlertShown: false, redAlertShown: false },
        { producto: 'Leche', cantidad: 20, categoria: 'Lácteos', proveedor: 'Proveedor B', orangeAlertShown: false, redAlertShown: false },
        { producto: 'Helado', cantidad: 15, categoria: 'Postres', proveedor: 'Proveedor C', orangeAlertShown: false, redAlertShown: false }
    ];

    function renderTable(filteredData = stockData) {
        stockTable.innerHTML = '';
        filteredData.forEach((item, index) => {
            const row = stockTable.insertRow();
            row.insertCell(0).textContent = item.producto;

            const cantidadCell = row.insertCell(1);
            cantidadCell.textContent = item.cantidad;
            cantidadCell.className = getColorClass(item.cantidad);

            row.insertCell(2).textContent = item.categoria;
            row.insertCell(3).textContent = item.proveedor;

            const actionsCell = row.insertCell(4);
            actionsCell.innerHTML = `
                <button onclick="decreaseStock(${index})">-</button>
                <button onclick="increaseStock(${index})">+</button>
            `;

            // Mostrar alerta solo la primera vez
            if (!item.redAlertShown && item.cantidad <= 5) {
                showModal("Cuidado, nos estamos quedando sin stock", 'red');
                item.redAlertShown = true;
                item.orangeAlertShown = true;  // Asegurarse de que no se muestre la alerta naranja después
            } else if (!item.orangeAlertShown && item.cantidad > 5 && item.cantidad <= 10) {
                showModal("Deberíamos administrar mejor nuestros recursos", 'orange');
                item.orangeAlertShown = true;
            } else if (item.cantidad > 10) {
                item.orangeAlertShown = false;
                item.redAlertShown = false;
            }
        });
    }

    function getColorClass(cantidad) {
        if (cantidad <= 5) {
            return 'stock-amount red';
        } else if (cantidad <= 10) {
            return 'stock-amount orange';
        } else {
            return 'stock-amount green';
        }
    }

    function showModal(message, type) {
        if (type === 'red') {
            modalImage.src = './img/inosuke.png'; // Ruta de la imagen para alerta roja
        } else if (type === 'orange') {
            modalImage.src = './img/nezuko.png'; // Ruta de la imagen para alerta naranja
        }

        modalMessage.textContent = message;
        modal.style.display = 'flex';
    }

    closeBtn.addEventListener('click', function () {
        modal.style.display = 'none';
    });

    window.increaseStock = function(index) {
        stockData[index].cantidad++;
        renderTable();
    };

    window.decreaseStock = function(index) {
        if (stockData[index].cantidad > 0) {
            stockData[index].cantidad--;
        }
        renderTable();
    };

    stockForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const producto = productoInput.value;
        const cantidad = parseInt(cantidadInput.value, 10);
        const categoria = categoriaSelect.value;
        const proveedor = proveedorSelect.value;

        stockData.push({ producto, cantidad, categoria, proveedor, orangeAlertShown: false, redAlertShown: false });

        stockForm.reset();
        renderTable();
        populateFilters(); // Actualizar los filtros después de añadir un nuevo producto
    });

    function populateFilters() {
        const categorias = new Set();
        const proveedores = new Set();

        stockData.forEach(item => {
            categorias.add(item.categoria);
            proveedores.add(item.proveedor);
        });

        // Limpiar y rellenar el select de categorías en el formulario
        categoriaSelect.innerHTML = '<option value="">Selecciona una categoría</option>';
        categorias.forEach(categoria => {
            const option = document.createElement('option');
            option.value = categoria;
            option.textContent = categoria;
            categoriaSelect.appendChild(option);
        });

        // Limpiar y rellenar el select de categorías en los filtros
        filtroCategoria.innerHTML = '<option value="todos">Todos</option>';
        categorias.forEach(categoria => {
            const option = document.createElement('option');
            option.value = categoria;
            option.textContent = categoria;
            filtroCategoria.appendChild(option);
        });

        // Limpiar y rellenar el select de proveedores en el formulario
        proveedorSelect.innerHTML = '<option value="">Selecciona un proveedor</option>';
        proveedores.forEach(proveedor => {
            const option = document.createElement('option');
            option.value = proveedor;
            option.textContent = proveedor;
            proveedorSelect.appendChild(option);
        });

        // Limpiar y rellenar el select de proveedores en los filtros
        filtroProveedor.innerHTML = '<option value="todos">Todos</option>';
        proveedores.forEach(proveedor => {
            const option = document.createElement('option');
            option.value = proveedor;
            option.textContent = proveedor;
            filtroProveedor.appendChild(option);
        });
    }

    function applyFilter() {
        const selectedCategoria = filtroCategoria.value;
        const selectedProveedor = filtroProveedor.value;

        const filteredData = stockData.filter(item => {
            const matchCategoria = selectedCategoria === 'todos' || item.categoria === selectedCategoria;
            const matchProveedor = selectedProveedor === 'todos' || item.proveedor === selectedProveedor;
            return matchCategoria && matchProveedor;
        });

        renderTable(filteredData);
    }

    aplicarFiltroBtn.addEventListener('click', applyFilter);

    // Inicializar la tabla y los filtros al cargar la página
    renderTable();
    populateFilters();
});

