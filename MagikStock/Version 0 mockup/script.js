let inventory = [
    { id: 1, name: "Cafe", quantity: 50, category: "Insumos", supplier: "Cafeteria" },
    { id: 2, name: "Mochi Oreo", quantity: 25, category: "Postres", supplier: "Rufiko" },
    { id: 3, name: "Gomu Gomu", quantity: 100, category: "Postres", supplier: "Pasteleria Inti Mapu" },
    { id: 4, name: "Helado", quantity: 75, category: "Insumos", supplier: "Heladeria" }
];

function renderInventory(items) {
    const table = document.getElementById("inventory-table");
    table.innerHTML = "";

    items.forEach(item => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.quantity}</td>
            <td>${item.category}</td>
            <td>${item.supplier}</td>
            <td>
                <button class="btn-outline" onclick="updateItem(${item.id}, 1)">+</button>
                <button class="btn-outline" onclick="updateItem(${item.id}, -1)">-</button>
            </td>
        `;
        table.appendChild(row);
    });
}

function addItem() {
    const name = document.getElementById("name").value;
    const quantity = parseInt(document.getElementById("quantity").value);
    const category = document.getElementById("category").value;
    const supplier = document.getElementById("supplier").value;

    if (name && quantity && category && supplier) {
        const newItem = {
            id: inventory.length + 1,
            name: name,
            quantity: quantity,
            category: category,
            supplier: supplier
        };

        inventory.push(newItem);
        renderInventory(inventory);

        // Limpiar campos
        document.getElementById("name").value = "";
        document.getElementById("quantity").value = "";
        document.getElementById("category").value = "";
        document.getElementById("supplier").value = "";
    }
}

function updateItem(id, change) {
    inventory = inventory.map(item => {
        if (item.id === id) {
            item.quantity += change;
        }
        return item;
    });
    renderInventory(inventory);
}

function filterItems() {
    const categoryFilter = document.getElementById("category-filter").value;
    const supplierFilter = document.getElementById("supplier-filter").value;

    const filteredInventory = inventory.filter(item => {
        return (categoryFilter === "" || item.category === categoryFilter) &&
               (supplierFilter === "" || item.supplier === supplierFilter);
    });

    renderInventory(filteredInventory);
}

// Inicializar con los elementos predeterminados
renderInventory(inventory);
