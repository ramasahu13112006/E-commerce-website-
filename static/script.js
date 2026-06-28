const API_URL = 'http://127.0.0.1:5000/api';
let products = [];
let cart = [];

async function fetchProducts() {
    try {
        const response = await fetch(`${API_URL}/products`);
        products = await response.json();
        displayProducts(products);
    } catch (error) {
        console.error("Error fetching products:", error);
    }
}

function displayProducts(productsToRender) {
    const grid = document.getElementById('products-grid');
    grid.innerHTML = '';
    if (productsToRender.length === 0) {
        grid.innerHTML = `<p class="loading">No products matched.</p>`;
        return;
    }
    productsToRender.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <img src="${product.image}" alt="${product.name}" class="product-image">
            <div>
                <h3 class="product-name">${product.name}</h3>
                <p class="product-desc">${product.description || ''}</p>
            </div>
            <div>
                <div class="product-price">₹${product.price.toFixed(2)}</div>
                <button class="add-btn" onclick="addToCart(${product.id})">Add to Cart</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

function handleSearch() {
    const query = document.getElementById('search-input').value.toLowerCase().trim();
    const filtered = products.filter(p => p.name.toLowerCase().includes(query) || p.description.toLowerCase().includes(query));
    displayProducts(filtered);
}

function toggleCart() {
    document.getElementById('cart-sidebar').classList.toggle('active');
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const cartItem = cart.find(item => item.id === productId);
    if (cartItem) {
        cartItem.quantity += 1;
    } else {
        cart.push({ ...product, quantity: 1 });
    }
    updateCartUI();
    const sidebar = document.getElementById('cart-sidebar');
    if (!sidebar.classList.contains('active')) sidebar.classList.add('active');
}

function updateCartUI() {
    document.getElementById('cart-count').innerText = cart.reduce((sum, item) => sum + item.quantity, 0);
    const cartContainer = document.getElementById('cart-items');
    cartContainer.innerHTML = '';
    let totalPrice = 0;
    if (cart.length === 0) cartContainer.innerHTML = `<p style="text-align:center; margin-top:20px;">Cart is empty</p>`;
    
    cart.forEach(item => {
        totalPrice += item.price * item.quantity;
        const itemEl = document.createElement('div');
        itemEl.className = 'cart-item';
        itemEl.innerHTML = `
            <div><h4>${item.name}</h4><small>₹${item.price} x ${item.quantity}</small></div>
            <span style="font-weight:bold;">₹${(item.price * item.quantity).toFixed(2)}</span>
        `;
        cartContainer.appendChild(itemEl);
    });
    document.getElementById('cart-total').innerText = totalPrice.toFixed(2);
}

function openCheckoutForm() {
    if (cart.length === 0) {
        alert("Aapka cart khali hai!");
        return;
    }
    document.getElementById('form-modal').classList.add('active');
}

function closeCheckoutForm() {
    document.getElementById('form-modal').classList.remove('remove');
    document.getElementById('form-modal').classList.remove('active');
}

async function handleCheckout(event) {
    event.preventDefault();
    
    const name = document.getElementById('cust-name').value;
    const email = document.getElementById('cust-email').value;
    const phone = document.getElementById('cust-phone').value;

    try {
        const response = await fetch(`${API_URL}/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cart: cart, name: name, email: email, phone: phone })
        });

        const result = await response.json();
        if (response.ok) {
            alert(`🎉 Order successful!\nEmail Notification: ${result.email_status}`);
            cart = [];
            updateCartUI();
            closeCheckoutForm();
            toggleCart();
        } else {
            alert("Error: " + result.error);
        }
    } catch (error) {
        console.error(error);
        alert("Server error!");
    }
}

window.onload = fetchProducts;
