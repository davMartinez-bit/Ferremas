// Página de Productos - JavaScript

// Variables globales
let productos = [];
let carrito = [];
let currentUser = null;
let favoritos = [];
let divisaSeleccionada = 'CLP';
let tasasCambio = {};
let cargandoDivisas = false;

// Inicialización
// Al cargar la página, obtener productos reales desde la API

document.addEventListener('DOMContentLoaded', async function() {
    try {
        // 1. Verificar estado de autenticación
        await checkUserAuthStatus();
        
        // 2. Cargar tasas de cambio del Banco Central
        await cargarTasasCambio();
        
        // 3. Cargar categorías
        await cargarCategorias();
        
        // 4. Cargar productos
        await cargarProductos();
        
        // 5. Cargar carrito si el usuario está autenticado
        if (currentUser) {
            await cargarCarrito();
            actualizarContadorCarrito();
        }
        
        // 6. Configurar event listeners
        configurarEventListeners();
        
        // 7. Configurar selector de divisas
        configurarSelectorDivisas();
        
        // 8. Configurar botón de prueba Webpay
        const testWebpayBtn = document.getElementById('test-webpay-btn');
        if (testWebpayBtn) {
            testWebpayBtn.addEventListener('click', testWebpayRedirect);
        }
        
    } catch (error) {
        console.error('Error durante la inicialización:', error);
        showNotification('Error al cargar la página', 'error');
    }
});

// Mostrar productos en la página
function mostrarProductos() {
    const grid = document.getElementById('productos-grid');
    if (!grid) {
        console.error('No se encontró el elemento productos-grid');
        return;
    }
    if (!productos || productos.length === 0) {
        grid.innerHTML = '<p>No hay productos disponibles.</p>';
        return;
    }
    
    grid.innerHTML = productos.map(producto => {
        const esFavorito = favoritos.some(fav => fav.producto_id === producto.id);
        return `
        <div class="producto-card">
            <div class="favorito-icon" onclick="toggleFavorite(this, ${producto.id})">
                <i class="${esFavorito ? 'fas' : 'far'} fa-heart"></i>
            </div>
            <img src="${producto.imagen || 'https://via.placeholder.com/300x250?text=Producto'}" alt="${producto.nombre}" class="producto-image" />
            <div class="producto-info">
                <h3 class="producto-nombre">${producto.nombre}</h3>
                <p class="producto-categoria">Categoría: ${producto.categoria ? producto.categoria.nombre : 'N/A'}</p>
                <p class="producto-precio">${mostrarPrecioProducto(producto.precio_actual)}</p>
                <div class="producto-actions">
                    <button class="btn-add-cart" onclick="agregarAlCarrito(${producto.id})">
                        <i class="fas fa-shopping-cart"></i> Agregar al Carrito
                    </button>
                </div>
            </div>
        </div>
    `}).join('');
}

// Funciones del carrito integradas con la API
async function agregarAlCarrito(productoId) {
    try {
        if (!currentUser) {
            showNotification('Debes iniciar sesión para agregar productos al carrito', 'warning');
            
            // Mostrar un modal o confirmación antes de redirigir
            const confirmar = confirm('¿Deseas ir a la página de inicio de sesión?');
            if (confirmar) {
                window.location.href = "/login";
            }
            return;
        }
        
        const producto = productos.find(p => p.id === productoId);
        if (!producto) {
            showNotification('Producto no encontrado', 'error');
            return;
        }
        
        // Llamar a la API para agregar al carrito
        const result = await API.carrito.add({ producto_id: productoId, cantidad: 1 });
        
        showNotification(`${producto.nombre} agregado al carrito`, 'success');
        
        // Recargar carrito y actualizar contador
        await cargarCarrito();
        actualizarContadorCarrito();
        
        // Abrir carrito para mostrar el producto agregado
        abrirCarrito();
        
    } catch (error) {
        console.error('Error en agregarAlCarrito:', error);
        
        // Manejar errores específicos
        if (error.message && error.message.includes('No autorizado')) {
            clearAuthData();
            updateAuthUI();
            showNotification('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning');
            
            const confirmar = confirm('¿Deseas ir a la página de inicio de sesión?');
            if (confirmar) {
                window.location.href = "/login";
            }
        } else {
            handleNetworkError(error);
        }
    }
}

function abrirCarrito() {
    if (!currentUser) {
        showNotification('Debes iniciar sesión para ver tu carrito', 'warning');
        if (confirm('¿Deseas ir a la página de inicio de sesión?')) {
            window.location.href = "/login";
        }
        return;
    }
    
    const sidebar = document.getElementById('cart-sidebar');
    const overlay = document.getElementById('cart-overlay');
    if (sidebar && overlay) {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        actualizarCarrito();
    }
}

function cerrarCarrito() {
    const sidebar = document.getElementById('cart-sidebar');
    const overlay = document.getElementById('cart-overlay');
    if (sidebar && overlay) {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
    }
}

async function actualizarCarrito() {
    const cartItems = document.getElementById('cart-items');
    const cartSubtotal = document.getElementById('cart-subtotal');
    const cartTax = document.getElementById('cart-tax');
    const cartTotal = document.getElementById('cart-total');
    if (!cartItems) return;
    if (!carrito || carrito.length === 0) {
        cartItems.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-bag"></i>
                <p>Tu carrito está vacío</p>
                <span>Agrega productos para comenzar</span>
            </div>
        `;
        if (cartSubtotal) cartSubtotal.textContent = '0';
        if (cartTax) cartTax.textContent = '0';
        if (cartTotal) cartTotal.textContent = '0';
        return;
    }
    cartItems.innerHTML = carrito.map(item => `
        <div class="cart-item">
            <img src="${item.producto?.imagen || 'https://via.placeholder.com/100x80?text=Producto'}" alt="${item.producto?.nombre || ''}" class="cart-item-image" />
            <div class="cart-item-details">
                <h4 class="cart-item-name">${item.producto?.nombre || ''}</h4>
                <p class="cart-item-price">${mostrarPrecioProducto(item.producto?.precio_actual)}</p>
                <div class="cart-item-quantity">
                    <button class="quantity-btn" onclick="cambiarCantidad(${item.id}, ${item.cantidad - 1})">
                        <i class="fas fa-minus"></i>
                    </button>
                    <span>${item.cantidad}</span>
                    <button class="quantity-btn" onclick="cambiarCantidad(${item.id}, ${item.cantidad + 1})">
                        <i class="fas fa-plus"></i>
                    </button>
                </div>
            </div>
            <button class="cart-item-remove" onclick="removerDelCarrito(${item.id})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `).join('');
    // Actualizar totales
    const subtotal = carrito.reduce((total, item) => total + ((item.producto?.precio_actual || 0) * item.cantidad), 0);
    const tax = subtotal * 0.19;
    const total = subtotal + tax;
    
    // Mostrar totales en la divisa seleccionada
    if (cartSubtotal) {
        if (divisaSeleccionada === 'CLP') {
            cartSubtotal.textContent = subtotal.toLocaleString();
        } else {
            const subtotalConvertido = convertirPrecio(subtotal, divisaSeleccionada);
            cartSubtotal.textContent = subtotalConvertido ? subtotalConvertido.toFixed(2) : 'N/A';
        }
    }
    
    if (cartTax) {
        if (divisaSeleccionada === 'CLP') {
            cartTax.textContent = tax.toLocaleString();
        } else {
            const taxConvertido = convertirPrecio(tax, divisaSeleccionada);
            cartTax.textContent = taxConvertido ? taxConvertido.toFixed(2) : 'N/A';
        }
    }
    
    if (cartTotal) {
        if (divisaSeleccionada === 'CLP') {
            cartTotal.textContent = total.toLocaleString();
        } else {
            const totalConvertido = convertirPrecio(total, divisaSeleccionada);
            cartTotal.textContent = totalConvertido ? totalConvertido.toFixed(2) : 'N/A';
        }
    }
}

async function cambiarCantidad(itemId, nuevaCantidad) {
    if (nuevaCantidad < 1) return;
    try {
        await API.carrito.update(itemId, { cantidad: nuevaCantidad });
        await cargarCarrito();
        actualizarContadorCarrito();
        actualizarCarrito();
    } catch (error) {
        handleNetworkError(error);
    }
}

async function removerDelCarrito(itemId) {
    try {
        await API.carrito.remove(itemId);
        await cargarCarrito();
        actualizarContadorCarrito();
        actualizarCarrito();
    } catch (error) {
        handleNetworkError(error);
    }
}

async function vaciarCarrito() {
    try {
        await API.carrito.clear();
        await cargarCarrito();
        actualizarContadorCarrito();
        actualizarCarrito();
    } catch (error) {
        handleNetworkError(error);
    }
}

async function cargarCarrito() {
    console.log('🛒 cargarCarrito iniciado...');
    console.log('👤 Estado del usuario:', currentUser ? currentUser.nombre : 'no autenticado');
    
    try {
        if (!currentUser) {
            console.log('❌ Usuario no autenticado, carrito vacío');
            carrito = [];
            return;
        }
        
        console.log('📤 Llamando a API.carrito.getAll...');
        carrito = await API.carrito.getAll();
        console.log(`✅ Carrito cargado: ${carrito.length} items`);
        
        // Log detallado de los items del carrito
        carrito.forEach((item, index) => {
            console.log(`  ${index + 1}. ${item.producto?.nombre || 'Producto desconocido'} x${item.cantidad}`);
        });
        
    } catch (error) {
        console.error('❌ Error cargando carrito:', error);
        
        // Si es un error de autorización, limpiar sesión
        if (error.message && error.message.includes('No autorizado')) {
            console.log('🔐 Error de autorización, limpiando sesión...');
            clearAuthData();
            updateAuthUI();
            showNotification('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning');
        } else {
            showNotification('Error al cargar el carrito', 'error');
        }
        
        carrito = [];
    }
}

function actualizarContadorCarrito() {
    console.log('🔢 actualizarContadorCarrito iniciado...');
    console.log('📦 Items en carrito:', carrito.length);
    
    const contador = document.getElementById('cart-count');
    if (!contador) {
        console.log('⚠️ Elemento cart-count no encontrado');
        return;
    }
    
    const totalItems = carrito.reduce((total, item) => total + (item.cantidad || 0), 0);
    console.log('📊 Total de items:', totalItems);
    
    if (totalItems > 0) {
        contador.textContent = totalItems;
        contador.style.display = 'block';
        console.log('✅ Contador actualizado:', totalItems);
    } else {
        contador.style.display = 'none';
        console.log('✅ Contador ocultado (carrito vacío)');
    }
}

// Funciones de autenticación
async function checkUserAuthStatus() {
    console.log('🔍 checkUserAuthStatus iniciado...');
    
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    console.log('📋 Estado actual:');
    console.log('  - Token presente:', token ? '✅' : '❌');
    console.log('  - userData presente:', userData ? '✅' : '❌');
    
    if (!token || !userData) {
        console.log('❌ No hay token o userData, usuario no autenticado');
        currentUser = null;
        updateAuthUI();
        return;
    }
    
    // Para tokens simulados, usar directamente los datos del localStorage
    if (token.includes('mock-')) {
        console.log('🔧 Token simulado detectado, usando datos del localStorage...');
        try {
            const parsedUser = JSON.parse(userData);
            currentUser = parsedUser;
            console.log('✅ Usuario simulado cargado:', currentUser.nombre);
            updateAuthUI();
            return;
        } catch (error) {
            console.error('❌ Error al parsear datos simulados:', error);
            clearAuthData();
            currentUser = null;
            updateAuthUI();
            return;
        }
    }
    
    // Para tokens reales, verificar con el servidor
    try {
        console.log('🔍 Verificando token con el servidor...');
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuarios/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            console.log('✅ Token válido, usuario:', user.nombre);
            
            // Actualizar datos del usuario en localStorage
            localStorage.setItem('userData', JSON.stringify(user));
            localStorage.setItem('rol', user.rol);
            
            currentUser = user;
            console.log('✅ Usuario autenticado:', currentUser.nombre, `(${currentUser.rol})`);
        } else {
            console.log('❌ Token inválido, limpiando datos...');
            clearAuthData();
            currentUser = null;
        }
    } catch (error) {
        console.error('❌ Error al verificar token:', error);
        // En caso de error de red, mantener la sesión si hay datos válidos
        try {
            const parsedUser = JSON.parse(userData);
            if (parsedUser.id && parsedUser.email && parsedUser.rol) {
                console.log('⚠️ Error de red, manteniendo sesión con datos locales...');
                currentUser = parsedUser;
            } else {
                console.log('❌ Datos locales inválidos, limpiando sesión...');
                clearAuthData();
                currentUser = null;
            }
        } catch (parseError) {
            console.error('❌ Error al parsear datos locales:', parseError);
            clearAuthData();
            currentUser = null;
        }
    }
    
    console.log('🎯 checkUserAuthStatus completado. currentUser:', currentUser ? currentUser.nombre : 'null');
    updateAuthUI();
}

function updateAuthUI() {
    console.log('🎨 Actualizando UI de autenticación...');
    
    const authLinks = document.getElementById('auth-links');
    const userInfo = document.getElementById('user-info');
    const userName = document.getElementById('user-name');
    const dashboardBtnContainer = document.getElementById('dashboard-btn-container');
    
    console.log('📋 Elementos encontrados:');
    console.log('  - auth-links:', authLinks ? '✅' : '❌');
    console.log('  - user-info:', userInfo ? '✅' : '❌');
    console.log('  - user-name:', userName ? '✅' : '❌');
    
    if (currentUser) {
        console.log('👤 Usuario autenticado, mostrando información de usuario...');
        
        if (userName) {
            userName.textContent = currentUser.nombre || currentUser.email;
            console.log('✅ Nombre de usuario actualizado:', userName.textContent);
        }
        
        if (userInfo) {
            userInfo.style.display = 'flex';
            console.log('✅ Información de usuario mostrada');
        }
        
        // Determinar el dashboard según el rol
        let dashboardHref = '/html/clientedashboard.html';
        let dashboardText = 'Ir a mi Dashboard';
        let dashboardIcon = 'fas fa-user-circle';
        if (currentUser.rol === 'admin') {
            dashboardHref = '/html/emp_dashboard.html';
            dashboardText = 'Ir a Administración';
            dashboardIcon = 'fas fa-cog';
        } else if (currentUser.rol === 'empleado') {
            dashboardHref = '/html/emp_dashboard.html';
            dashboardText = 'Ir a Panel Empleado';
            dashboardIcon = 'fas fa-briefcase';
        }
        if (dashboardBtnContainer) {
            dashboardBtnContainer.innerHTML = `
                <a href="${dashboardHref}" class="btn btn-dashboard" style="margin-right: 10px; display: inline-flex; align-items: center; gap: 6px; background: #007bff; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-weight: bold;">
                    <i class="${dashboardIcon}"></i> ${dashboardText}
                </a>
            `;
        }
        
    } else {
        console.log('🚪 Usuario no autenticado, mostrando opciones de login...');
        
        if (userInfo) {
            userInfo.style.display = 'none';
            console.log('✅ Información de usuario ocultada');
        }
        
        if (authLinks) {
            authLinks.innerHTML = `
                <a href="/login" class="nav-link">
                    <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
                </a>
                <a href="/register" class="nav-link">
                    <i class="fas fa-user-plus"></i> Registrarse
                </a>
            `;
            console.log('✅ Enlaces de login/registro mostrados');
        }
        
        if (dashboardBtnContainer) {
            dashboardBtnContainer.innerHTML = `
                <a href="/login.html" class="btn btn-dashboard" style="margin-right: 10px; display: inline-flex; align-items: center; gap: 6px; background: #007bff; color: white; padding: 8px 16px; border-radius: 4px; text-decoration: none; font-weight: bold;">
                    <i class="fas fa-sign-in-alt"></i> Iniciar sesión
                </a>
            `;
        }
    }
    
    console.log('✅ updateAuthUI completado');
}

// Función para limpiar datos de autenticación
function clearAuthData() {
    console.log('🧹 Limpiando datos de autenticación...');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    localStorage.removeItem('rol');
    currentUser = null;
    console.log('✅ Datos de autenticación limpiados');
}

function logout() {
    console.log('🚪 Logout iniciado...');
    clearAuthData();
    showNotification('Sesión cerrada exitosamente', 'success');
    
    // Redirigir a la página principal
    setTimeout(() => {
        window.location.href = '/';
    }, 1500);
}

// Configurar event listeners
function configurarEventListeners() {
    // Carrito
    const toggleCart = document.getElementById('toggle-cart');
    const closeCart = document.getElementById('close-cart');
    const cartOverlay = document.getElementById('cart-overlay');
    const clearCart = document.getElementById('clear-cart');
    const checkoutBtn = document.getElementById('checkout-btn');
    
    if (toggleCart) toggleCart.addEventListener('click', abrirCarrito);
    if (closeCart) closeCart.addEventListener('click', cerrarCarrito);
    if (cartOverlay) cartOverlay.addEventListener('click', cerrarCarrito);
    if (clearCart) clearCart.addEventListener('click', vaciarCarrito);
    if (checkoutBtn) checkoutBtn.addEventListener('click', finalizarCompra);
    
    // Filtros
    const filtroForm = document.getElementById('filtro-form');
    if (filtroForm) {
        filtroForm.addEventListener('submit', function(e) {
            e.preventDefault();
            filtrarProductos();
        });
    }
}

function normalizarTexto(texto) {
    return (texto || '').toString().trim().toLowerCase().normalize('NFD').replace(/[0-\u036f]/g, '');
}

function filtrarProductos() {
    const nombre = normalizarTexto(document.getElementById('filtro-nombre')?.value);
    const categoriaId = document.getElementById('filtro-categoria')?.value || '';
    const precioMin = document.getElementById('filtro-precio-min')?.value || '';
    const precioMax = document.getElementById('filtro-precio-max')?.value || '';
    
    const productosFiltrados = productos.filter(producto => {
        // Filtro por nombre
        const matchNombre = !nombre || normalizarTexto(producto.nombre).includes(nombre);
        // Filtro por categoría (por ID)
        const matchCategoria = !categoriaId || (producto.categoria && String(producto.categoria.id) === categoriaId);
        // Filtros por precio
        const matchPrecioMin = !precioMin || producto.precio_actual >= parseFloat(precioMin);
        const matchPrecioMax = !precioMax || producto.precio_actual <= parseFloat(precioMax);
        return matchNombre && matchCategoria && matchPrecioMin && matchPrecioMax;
    });
    
    mostrarProductosFiltrados(productosFiltrados);
}

function mostrarProductosFiltrados(productosFiltrados) {
    const grid = document.getElementById('productos-grid');
    if (!grid) return;
    
    if (productosFiltrados.length === 0) {
        grid.innerHTML = `
            <div class="no-products">
                <i class="fas fa-search"></i>
                <h3>No se encontraron productos</h3>
                <p>Intenta ajustar los filtros de búsqueda</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = productosFiltrados.map(producto => `
        <div class="producto-card">
            <img src="${producto.imagen}" alt="${producto.nombre}" class="producto-image" />
            <div class="producto-info">
                <h3 class="producto-nombre">${producto.nombre}</h3>
                <p class="producto-categoria">Categoría: ${producto.categoria}</p>
                <p class="producto-precio">${mostrarPrecioProducto(producto.precio_actual)}</p>
                <div class="producto-actions">
                    <button class="btn-add-cart" onclick="agregarAlCarrito(${producto.id})">
                        <i class="fas fa-shopping-cart"></i> Agregar al Carrito
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 300px;
    `;
    
    // Colores según el tipo
    switch (type) {
        case 'success':
            notification.style.backgroundColor = '#28a745';
            break;
        case 'error':
            notification.style.backgroundColor = '#dc3545';
            break;
        case 'warning':
            notification.style.backgroundColor = '#ffc107';
            notification.style.color = '#212529';
            break;
        default:
            notification.style.backgroundColor = '#17a2b8';
    }
    
    notification.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Mostrar con animación
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Función para obtener icono de notificación
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

// Función para finalizar compra
async function finalizarCompra() {
    if (!currentUser) {
        showNotification('Debes iniciar sesión para finalizar tu compra', 'warning');
        if (confirm('¿Deseas ir a la página de inicio de sesión?')) {
            window.location.href = "/login";
        }
        return;
    }
    
    if (!carrito || carrito.length === 0) {
        showNotification('Tu carrito está vacío', 'warning');
        return;
    }
    
    try {
        showNotification('Iniciando pago seguro con Webpay...', 'info');
        
        const response = await API.pagos.createWebpayTransaction();
        
        if (response && response.url && response.token) {
            // Crear un formulario temporal para hacer POST a Webpay
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = 'https://webpay3gint.transbank.cl/webpayserver/init_transaction.cgi';
            form.target = '_blank';
            
            // Agregar el token como campo oculto
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'token_ws';
            tokenInput.value = response.token;
            form.appendChild(tokenInput);
            
            // Agregar el formulario al DOM y enviarlo
            document.body.appendChild(form);
            form.submit();
            
            // Limpiar el formulario
            document.body.removeChild(form);
            
            const totalFormateado = response.total ? `$${response.total.toLocaleString()}` : '';
            showNotification(`Página de pago abierta. Total: ${totalFormateado}`, 'success');
        } else {
            showNotification('No se pudo iniciar el pago. Intenta de nuevo.', 'error');
        }
    } catch (error) {
        console.error('Error al iniciar el proceso de pago:', error);
        showNotification(error.message || 'Error al procesar la compra.', 'error');
    }
}

// Función para manejar errores de red
function handleNetworkError(error) {
    let mensaje = 'Error de conexión. Por favor, verifica tu conexión a internet.';
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        mensaje = 'No se pudo conectar con el servidor. Verifica que el servidor esté funcionando.';
    } else if (error.message.includes('Failed to fetch')) {
        mensaje = 'Error de conexión con el servidor. Intenta nuevamente.';
    } else if (error.message.includes('timeout')) {
        mensaje = 'La solicitud tardó demasiado. Intenta nuevamente.';
    } else if (error.message) {
        mensaje = `Error: ${error.message}`;
    }
    
    showNotification(mensaje, 'error');
}

// Función de prueba para Webpay
async function testWebpayRedirect() {
    if (!currentUser) {
        showNotification('Debes iniciar sesión para probar Webpay', 'warning');
        return;
    }
    
    if (!carrito || carrito.length === 0) {
        showNotification('Agrega productos al carrito antes de probar Webpay', 'warning');
        return;
    }
    
    try {
        showNotification('Iniciando prueba de Webpay...', 'info');
        
        const response = await API.pagos.createWebpayTransaction();
        
        if (response && response.url && response.token) {
            // Crear formulario temporal para POST a Webpay
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = 'https://webpay3gint.transbank.cl/webpayserver/init_transaction.cgi';
            form.target = '_blank';
            
            const tokenInput = document.createElement('input');
            tokenInput.type = 'hidden';
            tokenInput.name = 'token_ws';
            tokenInput.value = response.token;
            form.appendChild(tokenInput);
            
            document.body.appendChild(form);
            form.submit();
            document.body.removeChild(form);
            
            showNotification('Página de prueba de Webpay abierta', 'success');
        } else {
            showNotification('Error al crear transacción de prueba', 'error');
        }
    } catch (error) {
        console.error('Error en prueba de Webpay:', error);
        showNotification('Error al probar Webpay', 'error');
    }
}

async function toggleFavorite(element, productoId) {
    if (!currentUser) {
        showNotification('Debes iniciar sesión para agregar favoritos', 'warning');
        return;
    }

    const heartIcon = element.querySelector('i');
    if (!heartIcon) return;

    // Cambiar el ícono inmediatamente para una respuesta visual rápida
    heartIcon.classList.toggle('far');
    heartIcon.classList.toggle('fas');

    try {
        // Usar el endpoint toggle que maneja agregar/eliminar automáticamente
        const result = await API.favoritos.toggle(productoId);
        
        if (result.status === 'agregado') {
            showNotification('Agregado a favoritos', 'success');
            // Actualizar la lista local de favoritos
            favoritos.push({
                producto_id: productoId,
                id: Date.now() // ID temporal
            });
        } else if (result.status === 'eliminado') {
            showNotification('Eliminado de favoritos', 'info');
            // Actualizar la lista local de favoritos
            favoritos = favoritos.filter(fav => fav.producto_id !== productoId);
        }
    } catch (error) {
        // Si hay un error, revertir el cambio visual
        heartIcon.classList.toggle('far');
        heartIcon.classList.toggle('fas');
        showNotification('No se pudo actualizar el favorito', 'error');
        console.error('Error al cambiar favorito:', error);
    }
}

// Función para cargar productos
async function cargarProductos() {
    try {
        productos = await API.productos.getAll();
        
        // Cargar favoritos si el usuario está autenticado
        if (currentUser) {
            try {
                favoritos = await API.favoritos.getAll();
            } catch (error) {
                favoritos = [];
            }
        }
        
        mostrarProductos();
        
    } catch (error) {
        console.error('Error al cargar productos:', error);
        showNotification('Error al cargar productos', 'error');
        productos = [];
        favoritos = [];
    }
}

// Funciones para manejo de divisas
async function cargarTasasCambio() {
    if (cargandoDivisas) return;
    
    cargandoDivisas = true;
    
    try {
        const resultado = await API.divisas.getAll();
        
        // Procesar las tasas de cambio
        resultado.forEach(divisa => {
            if (!divisa.error && divisa.valor_clp) {
                tasasCambio[divisa.moneda] = divisa.valor_clp;
            }
        });
        
        // Actualizar la información de tasa de cambio
        actualizarInfoTasaCambio();
        
        // Si hay productos cargados, actualizar sus precios
        if (productos.length > 0) {
            mostrarProductos();
        }
        
    } catch (error) {
        console.error('Error al cargar tasas de cambio:', error);
        showNotification('Error al cargar tasas de cambio', 'error');
    } finally {
        cargandoDivisas = false;
    }
}

function actualizarInfoTasaCambio() {
    const infoElement = document.getElementById('tasa-cambio-info');
    if (!infoElement) return;
    
    if (divisaSeleccionada === 'CLP') {
        infoElement.innerHTML = '<small>Tasa de cambio actualizada del Banco Central de Chile</small>';
    } else {
        const tasa = tasasCambio[divisaSeleccionada];
        if (tasa) {
            infoElement.innerHTML = `<small>1 ${divisaSeleccionada} = $${tasa.toLocaleString()} CLP</small>`;
        } else {
            infoElement.innerHTML = '<small>Error al cargar tasa de cambio</small>';
        }
    }
}

function convertirPrecio(precioCLP, monedaDestino) {
    if (monedaDestino === 'CLP') {
        return precioCLP;
    }
    
    const tasa = tasasCambio[monedaDestino];
    if (!tasa || tasa <= 0) {
        return null;
    }
    
    return precioCLP / tasa;
}

function formatearPrecio(precio, moneda) {
    if (precio === null || precio === undefined) {
        return 'N/A';
    }
    
    const simbolos = {
        'CLP': '$',
        'USD': 'US$',
        'EUR': '€'
    };
    
    const simbolo = simbolos[moneda] || '$';
    
    if (moneda === 'CLP') {
        return `${simbolo}${precio.toLocaleString()}`;
    } else {
        return `${simbolo}${precio.toFixed(2)}`;
    }
}

function mostrarPrecioProducto(precioCLP) {
    if (divisaSeleccionada === 'CLP') {
        return `<span class="precio-principal">${formatearPrecio(precioCLP, 'CLP')}</span>`;
    }
    
    const precioConvertido = convertirPrecio(precioCLP, divisaSeleccionada);
    if (precioConvertido === null) {
        return `<span class="precio-principal">${formatearPrecio(precioCLP, 'CLP')}</span>`;
    }
    
    return `
        <span class="precio-principal">${formatearPrecio(precioConvertido, divisaSeleccionada)}</span>
        <span class="precio-secundario">${formatearPrecio(precioCLP, 'CLP')}</span>
    `;
}

function configurarSelectorDivisas() {
    const selectorDivisa = document.getElementById('selector-divisa');
    if (!selectorDivisa) return;
    
    // Establecer valor inicial
    selectorDivisa.value = divisaSeleccionada;
    
    // Agregar event listener para cambio de divisa
    selectorDivisa.addEventListener('change', async function(e) {
        const nuevaDivisa = e.target.value;
        
        divisaSeleccionada = nuevaDivisa;
        
        // Si es la primera vez que se selecciona una divisa extranjera, cargar tasas
        if (nuevaDivisa !== 'CLP' && !tasasCambio[nuevaDivisa]) {
            await cargarTasasCambio();
        }
        
        // Actualizar información de tasa de cambio
        actualizarInfoTasaCambio();
        
        // Actualizar precios de productos
        if (productos.length > 0) {
            mostrarProductos();
        }
        
        // Actualizar carrito si está abierto
        if (document.getElementById('cart-sidebar').classList.contains('open')) {
            actualizarCarrito();
        }
        
        showNotification(`Moneda cambiada a ${nuevaDivisa}`, 'success');
    });
}

// Función para cargar categorías dinámicamente
async function cargarCategorias() {
    try {
        const categorias = await API.productos.getCategorias();
        
        const selectCategoria = document.getElementById('filtro-categoria');
        if (!selectCategoria) {
            return;
        }
        
        selectCategoria.innerHTML = '<option value="">Todas las categorías</option>';
        
        if (Array.isArray(categorias) && categorias.length > 0) {
            categorias.forEach((categoria, index) => {
                const option = document.createElement('option');
                option.value = categoria.id;
                option.textContent = categoria.nombre;
                selectCategoria.appendChild(option);
                
                // Subcategorías
                if (categoria.subcategorias && categoria.subcategorias.length > 0) {
                    categoria.subcategorias.forEach(subcategoria => {
                        const subOption = document.createElement('option');
                        subOption.value = subcategoria.id;
                        subOption.textContent = `  └ ${subcategoria.nombre}`;
                        selectCategoria.appendChild(subOption);
                    });
                }
            });
        }
        
    } catch (error) {
        console.error('Error al cargar categorías:', error);
        showNotification('Error al cargar categorías', 'error');
    }
} 
 
