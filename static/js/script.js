document.addEventListener("DOMContentLoaded", function () {
    loadProducts();
    loadCustomers();
    loadOrders();

    document
        .getElementById("customer-select")
        .addEventListener("change", viewCart);
});

async function loadProducts() {
    const response = await fetch("/products");
    const products = await response.json();
    const productSelect = document.getElementById("product-select");
    const productList = document.getElementById("product-list");
    productList.innerHTML = "";

    products.forEach((product) => {
        const option = document.createElement("option");
        option.value = product.id;
        option.textContent = product.name;
        productSelect.appendChild(option);

        const li = document.createElement("li");
        li.textContent = `${product.name} - $${product.price.toFixed(2)}`;
        productList.appendChild(li);
    });
}

async function loadCustomers() {
    const response = await fetch("/customers");
    const customers = await response.json();
    const customerSelect = document.getElementById("customer-select");
    const customerList = document.getElementById("customer-list");
    customerList.innerHTML = "";

    customers.forEach((customer) => {
        const option = document.createElement("option");
        option.value = customer.id;
        option.textContent = customer.name;
        customerSelect.appendChild(option);

        const li = document.createElement("li");
        li.textContent = `${customer.name} (${customer.email})`;
        customerList.appendChild(li);
    });
}

async function loadOrders() {
    const response = await fetch("/orders");
    const orders = await response.json();
    const orderList = document.getElementById("order-list");
    orderList.innerHTML = "";

    orders.forEach((order) => {
        const li = document.createElement("li");
        li.textContent = `Order #${order.id} - Total: $${order.total.toFixed(
            2
        )}`;
        orderList.appendChild(li);
    });
}

async function addProduct() {
    const name = document.getElementById("product-name").value;
    const price = parseFloat(document.getElementById("product-price").value);

    if (name && !isNaN(price)) {
        await fetch("/products", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, price }),
        });

        document.getElementById("product-name").value = "";
        document.getElementById("product-price").value = "";
        loadProducts();
    } else {
        alert("Please enter valid product details.");
    }
}

async function addCustomer() {
    const name = document.getElementById("customer-name").value;
    const email = document.getElementById("customer-email").value;

    if (name && email) {
        await fetch("/customers", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ name, email }),
        });

        document.getElementById("customer-name").value = "";
        document.getElementById("customer-email").value = "";
        loadCustomers();
    } else {
        alert("Please enter valid customer details.");
    }
}

async function addToCart() {
    const customerSelect = document.getElementById("customer-select");
    const productSelect = document.getElementById("product-select");
    let customerId = parseInt(customerSelect.value);
    let productId = parseInt(productSelect.value);
    customerId = parseFloat(customerId);
    productId = parseFloat(productId);

    if (!isNaN(customerId) && !isNaN(productId)) {
        await fetch(`/customers/${customerId}/cart`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ product_id: productId }),
        });

        viewCart();
    } else {
        alert("Please select a customer and a product.");
    }
}

async function viewCart() {
    const customerSelect = document.getElementById("customer-select");
    let customerId = parseInt(customerSelect.value);
    customerId = parseFloat(customerId);

    if (!isNaN(customerId)) {
        const response = await fetch(`/customers/${customerId}/cart`);
        const cartItems = await response.json();
        const cartList = document.getElementById("cart-list");
        cartList.innerHTML = "";

        cartItems.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = `${item.name} - $${item.price.toFixed(2)}`;
            cartList.appendChild(li);
        });
    }
}

async function checkout() {
    const customerSelect = document.getElementById("customer-select");
    let customerId = parseInt(customerSelect.value);
    customerId = parseFloat(customerId);

    if (!isNaN(customerId)) {
        await fetch(`/customers/${customerId}/checkout`, {
            method: "POST",
        });

        viewCart();
        loadOrders();
    } else {
        alert("Please select a customer.");
    }
}
