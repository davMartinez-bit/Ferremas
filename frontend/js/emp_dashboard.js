// Dashboard de Administrador - JavaScript

// Configuración de la API - usar la configuración de config.js
// const API_BASE_URL = 'http://localhost:8000/api'; // REMOVIDO - usar API_CONFIG.BASE_URL
let currentAdmin = null;
let currentEditingProduct = null;
let currentEditingUser = null;
let currentOrderDetails = null;

// Variables globales para el chat
let currentChatId = null;
let chatsList = [];
let chatRefreshInterval = null;

// Función de logout - definida al inicio para estar disponible inmediatamente
function logout() {
    console.log('🔓 Cerrando sesión de administrador...');
    clearAuthData();
    window.location.href = "/login.html";
}

// Función para limpiar datos de autenticación
function clearAuthData() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    localStorage.removeItem('rol');
    console.log('🧹 Datos de autenticación limpiados');
}

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== INICIALIZANDO DASHBOARD DE ADMIN ===');
    
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    const rol = localStorage.getItem('rol');
    
    console.log('Token encontrado:', token ? 'Sí' : 'No');
    console.log('Rol:', rol);
    
    // Verificar que hay token y que el rol es admin
    if (!token || !userData || rol !== 'admin') {
        console.log('❌ No hay token, userData o rol incorrecto, redirigiendo al login...');
        clearAuthData();
        window.location.href = "/login.html";
        return;
    }
    
    // Verificar si el token es válido antes de continuar
    checkTokenValidity().then(isValid => {
        if (!isValid) {
            console.log('❌ Token inválido, redirigiendo al login...');
            clearAuthData();
            window.location.href = "/login.html";
            return;
        }
        
        console.log('✅ Token válido, inicializando dashboard de admin...');
        initializeAdminDashboard();
    });
});

// Inicializar dashboard de administrador
function initializeAdminDashboard() {
    console.log('🚀 Inicializando dashboard de administrador...');
    
    // Cargar datos del administrador
    loadAdminData();
    
    // Cargar datos del dashboard
    loadDashboardData();
    
    // Configurar navegación del sidebar
    setupSidebarNavigation();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Inicializar gráficos
    initializeCharts();
    
    console.log('✅ Dashboard de admin inicializado correctamente');
}

// Configurar navegación del sidebar
function setupSidebarNavigation() {
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover clase activa de todos los enlaces
            sidebarLinks.forEach(l => l.classList.remove('active'));
            
            // Agregar clase activa al enlace clickeado
            this.classList.add('active');
            
            // Mostrar la sección correspondiente
            const target = this.getAttribute('data-section');
            showSection(target);
        });
    });
    
    // Mostrar sección por defecto
    showSection('resumen');
}

// Mostrar sección específica
function showSection(sectionName) {
    console.log('Mostrando sección:', sectionName);
    
    // Ocultar todas las secciones
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.style.display = 'none';
        section.classList.remove('active');
    });
    
    // Mostrar la sección seleccionada
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.style.display = 'block';
        targetSection.classList.add('active');
        console.log('✅ Sección mostrada:', sectionName);
        
        // Cargar datos específicos de la sección
        loadSectionData(sectionName);
    } else {
        console.error('❌ Sección no encontrada:', sectionName);
    }
}

// Cargar datos específicos de cada sección
function loadSectionData(sectionName) {
    switch(sectionName) {
        case 'resumen':
            loadDashboardStats();
            loadRecentOrders();
            loadLowStockProducts();
            break;
        case 'productos':
            loadProducts();
            break;
        case 'usuarios':
            loadUsers();
            break;
        case 'pedidos':
            loadOrders();
            break;
        case 'reportes':
            loadReports();
            break;
    }
}

// Configurar event listeners
function setupEventListeners() {
    // Formularios
    document.getElementById('productForm')?.addEventListener('submit', handleProductSubmit);
    document.getElementById('userForm')?.addEventListener('submit', handleUserSubmit);
    document.getElementById('contactForm')?.addEventListener('submit', handleContactSubmit);
    document.getElementById('generalConfigForm')?.addEventListener('submit', handleGeneralConfig);
    
    // Filtros
    document.getElementById('productSearch')?.addEventListener('input', filterProducts);
    document.getElementById('userSearch')?.addEventListener('input', filterUsers);
    document.getElementById('orderSearch')?.addEventListener('input', filterOrders);
    
    // Botón de logout
    const logoutBtn = document.querySelector('.btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }
}

// Cargar datos del administrador
async function loadAdminData() {
    try {
        console.log('🔍 Cargando datos del administrador...');
        const token = localStorage.getItem('authToken');
        
        // Verificar si es un token simulado
        if (token && token.includes('mock-')) {
            console.log('🔧 Token simulado detectado, usando datos del localStorage...');
            const userData = localStorage.getItem('userData');
            if (userData) {
                currentAdmin = JSON.parse(userData);
                console.log('Admin simulado cargado:', currentAdmin);
                updateAdminInterface();
                return;
            }
        }
        
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuarios/me`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            currentAdmin = await response.json();
            console.log('✅ Datos de admin cargados:', currentAdmin.nombre);
            updateAdminInterface();
        } else if (response.status === 401) {
            console.log('❌ Token inválido, redirigiendo al login...');
            clearAuthData();
            window.location.href = "/login.html";
            return;
        } else {
            throw new Error('Error al cargar datos del administrador');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al cargar datos del administrador', 'error');
    }
}

// Actualizar interfaz del administrador
function updateAdminInterface() {
    if (currentAdmin) {
        document.getElementById('adminName').textContent = currentAdmin.nombre || 'Administrador';
    }
}

// Verificar validez del token
async function checkTokenValidity() {
    try {
    const token = localStorage.getItem('authToken');
        
        // Si es un token simulado, considerarlo válido
        if (token && token.includes('mock-')) {
            console.log('🔧 Token simulado detectado, considerando válido');
            return true;
        }
        
    if (!token) {
        console.log('❌ No hay token');
        return false;
    }
    
        const response = await fetch(`${API_CONFIG.BASE_URL}/usuarios/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            console.log('✅ Token válido');
            return true;
        } else {
            console.log('❌ Token inválido');
            return false;
        }
    } catch (error) {
        console.error('❌ Error verificando token:', error);
        return false;
    }
}

// Cargar datos del dashboard
async function loadDashboardData() {
    try {
        console.log('📊 Cargando datos del dashboard...');
        
        // Verificar si es un token simulado
        const token = localStorage.getItem('authToken');
        if (token && token.includes('mock-')) {
            console.log('🔧 Token simulado detectado, cargando datos simulados...');
            loadSimulatedDashboardData();
            return;
        }
        
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            updateDashboardStats(stats);
        } else {
            throw new Error('Error al cargar estadísticas del dashboard');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al cargar datos del dashboard', 'error');
    }
}

// Cargar estadísticas del dashboard
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/stats`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            updateDashboardStats(stats);
        }
    } catch (error) {
        console.error('❌ Error cargando estadísticas:', error);
    }
}

// Actualizar estadísticas en el dashboard
function updateDashboardStats(stats) {
    document.getElementById('totalUsuarios').textContent = stats.total_usuarios || 0;
    document.getElementById('totalPedidos').textContent = stats.total_pedidos || 0;
    document.getElementById('totalProductos').textContent = stats.total_productos || 0;
    document.getElementById('ventasHoy').textContent = `$${(stats.ventas_mes || 0).toLocaleString()}`;
}

// Cargar pedidos recientes
async function loadRecentOrders() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/pedidos?limit=5`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const orders = await response.json();
            console.log('✅ Pedidos recientes cargados:', orders);
            displayRecentOrders(orders);
        }
    } catch (error) {
        console.error('❌ Error cargando pedidos recientes:', error);
    }
}

// Mostrar pedidos recientes
function displayRecentOrders(orders) {
    const container = document.getElementById('recentOrdersList');
    if (!container) return;
    
    if (!orders || orders.length === 0) {
        container.innerHTML = '<p class="no-data">No hay pedidos recientes</p>';
        return;
    }
    
    container.innerHTML = orders.map(order => `
        <div class="order-item">
            <div class="order-info">
                <h4>Pedido #${order.numero_pedido || order.id}</h4>
                <p class="order-customer">Cliente: ${order.cliente_nombre || 'N/A'}</p>
                <p class="order-date">${new Date(order.fecha_creacion).toLocaleDateString('es-ES')}</p>
            </div>
            <div class="order-status">
                <span class="status-badge ${order.estado?.toLowerCase()}">${order.estado || 'PENDIENTE'}</span>
                <p class="order-total">$${(order.total || 0).toLocaleString()}</p>
            </div>
        </div>
    `).join('');
}

// Cargar productos con bajo stock
async function loadLowStockProducts() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/productos/?stock_max=10`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const products = await response.json();
            console.log('✅ Productos con bajo stock cargados:', products);
            displayLowStockProducts(products);
        }
    } catch (error) {
        console.error('❌ Error cargando productos con bajo stock:', error);
    }
}

// Mostrar productos con bajo stock
function displayLowStockProducts(products) {
    const container = document.getElementById('lowStockList');
    if (!container) return;
    
    if (!products || products.length === 0) {
        container.innerHTML = '<p class="no-data">No hay productos con bajo stock</p>';
        return;
    }
    
    container.innerHTML = products.map(product => `
        <div class="product-item">
            <div class="product-info">
                <h4>${product.nombre}</h4>
                <p class="product-code">Código: ${product.codigo}</p>
            </div>
            <div class="product-stock">
                <span class="stock-badge low">${product.stock} unidades</span>
            </div>
        </div>
    `).join('');
}

// ===== GESTIÓN DE PRODUCTOS =====

// Cargar productos
async function loadProducts() {
    try {
        console.log('📦 Cargando productos...');
        
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${API_CONFIG.BASE_URL}/productos/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const products = await response.json();
            console.log('✅ Productos cargados:', products);
            displayProductsTable(products);
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Error al cargar productos:', error);
        showNotification('Error al cargar productos', 'error');
    }
}

// Mostrar tabla de productos
function displayProductsTable(products) {
    const container = document.getElementById('productsTable');
    if (!container) return;
    
    if (!products || products.length === 0) {
        container.innerHTML = '<p class="no-data">No hay productos disponibles</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Nombre</th>
                    <th>Categoría</th>
                    <th>Stock</th>
                    <th>Precio</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${products.map(product => `
                    <tr>
                        <td>${product.codigo || 'N/A'}</td>
                        <td>${product.nombre || 'N/A'}</td>
                        <td>${product.categoria?.nombre || 'N/A'}</td>
                        <td>
                            <span class="stock-badge ${getStockLevel(product.stock)}">${product.stock || 0}</span>
                        </td>
                        <td>$${(product.precio_actual || 0).toLocaleString()}</td>
                        <td>
                            <span class="status-badge ${product.activo ? 'active' : 'inactive'}">
                                ${product.activo ? 'Activo' : 'Inactivo'}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button onclick="editProduct('${product.codigo}')" class="btn-edit" title="Editar">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="deleteProduct('${product.codigo}')" class="btn-delete" title="Eliminar">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Obtener nivel de stock
function getStockLevel(stock) {
    if (stock <= 5) return 'bajo';
    if (stock <= 20) return 'medio';
    return 'alto';
}

// Filtrar productos
function filterProducts() {
    const searchTerm = document.getElementById('productSearch')?.value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter')?.value;
    const stockFilter = document.getElementById('stockFilter')?.value;
    
    const rows = document.querySelectorAll('#productsTable tbody tr');
    
    rows.forEach(row => {
        const name = row.cells[1]?.textContent.toLowerCase();
        const category = row.cells[2]?.textContent.toLowerCase();
        const stock = parseInt(row.cells[3]?.textContent) || 0;
        
        let show = true;
        
        // Filtro por búsqueda
        if (searchTerm && !name.includes(searchTerm)) {
            show = false;
        }
        
        // Filtro por categoría
        if (categoryFilter && category !== categoryFilter.toLowerCase()) {
            show = false;
        }
        
        // Filtro por stock
        if (stockFilter) {
            if (stockFilter === 'bajo' && stock > 10) show = false;
            if (stockFilter === 'medio' && (stock <= 10 || stock > 50)) show = false;
            if (stockFilter === 'alto' && stock <= 50) show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

// Mostrar modal de agregar producto
function showAddProductModal() {
    document.getElementById('productModalTitle').textContent = 'Agregar Producto';
    document.getElementById('productForm').reset();
    currentEditingProduct = null;
    showModal('productModal');
}

// Mostrar modal de editar producto
async function editProduct(productCode) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/productos/${productCode}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const product = await response.json();
            currentEditingProduct = productCode;
            
            // Llenar formulario con datos del producto
            document.getElementById('productName').value = product.nombre;
            document.getElementById('productCategory').value = product.categoria;
            document.getElementById('productPrice').value = product.precio;
            document.getElementById('productStock').value = product.stock;
            document.getElementById('productDescription').value = product.descripcion || '';
            document.getElementById('productImage').value = product.imagen || '';
            
            document.getElementById('productModalTitle').textContent = 'Editar Producto';
            showModal('productModal');
        }
    } catch (error) {
        console.error('❌ Error cargando producto:', error);
        showNotification('Error al cargar producto', 'error');
    }
}

// Manejar envío del formulario de producto
async function handleProductSubmit(e) {
    e.preventDefault();
    
    const formData = {
        nombre: document.getElementById('productName').value,
        categoria: document.getElementById('productCategory').value,
        precio: parseFloat(document.getElementById('productPrice').value),
        stock: parseInt(document.getElementById('productStock').value),
        descripcion: document.getElementById('productDescription').value,
        imagen: document.getElementById('productImage').value
    };
    
    try {
        const url = currentEditingProduct 
            ? `${API_CONFIG.BASE_URL}/productos/${currentEditingProduct}`
            : `${API_CONFIG.BASE_URL}/productos/`;
        
        const method = currentEditingProduct ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showNotification(
                currentEditingProduct ? 'Producto actualizado correctamente' : 'Producto creado correctamente',
                'success'
            );
            closeModal('productModal');
            loadProducts();
            currentEditingProduct = null;
        } else {
            throw new Error('Error al guardar producto');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al guardar producto', 'error');
    }
}

// Eliminar producto
async function deleteProduct(productCode) {
    if (!confirm('¿Estás seguro de que quieres eliminar este producto?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/productos/${productCode}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            showNotification('Producto eliminado correctamente', 'success');
            loadProducts();
        } else {
            throw new Error('Error al eliminar producto');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al eliminar producto', 'error');
    }
}

// ===== GESTIÓN DE USUARIOS =====

// Cargar usuarios
async function loadUsers() {
    try {
        console.log('👥 Cargando usuarios...');
        
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/usuarios`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const users = await response.json();
            console.log('✅ Usuarios cargados:', users);
            displayUsersTable(users);
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Error al cargar usuarios:', error);
        showNotification('Error al cargar usuarios', 'error');
    }
}

// Mostrar tabla de usuarios
function displayUsersTable(users) {
    const container = document.getElementById('usersTable');
    if (!container) return;
    
    if (!users || users.length === 0) {
        container.innerHTML = '<p class="no-data">No hay usuarios registrados</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Email</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th>Fecha Registro</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(user => `
                    <tr>
                        <td>${user.id}</td>
                        <td>${user.nombre || user.username || 'N/A'}</td>
                        <td>${user.email}</td>
                        <td>
                            <span class="role-badge ${user.rol}">${user.rol}</span>
                        </td>
                        <td>
                            <span class="status-badge ${user.activo ? 'active' : 'inactive'}">
                                ${user.activo ? 'Activo' : 'Inactivo'}
                            </span>
                        </td>
                        <td>${new Date(user.fecha_creacion).toLocaleDateString('es-ES')}</td>
                        <td>
                            <div class="action-buttons">
                                <button onclick="editUser(${user.id})" class="btn-edit" title="Editar">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button onclick="toggleUserStatus(${user.id})" class="btn-toggle" title="Cambiar Estado">
                                    <i class="fas fa-toggle-on"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Filtrar usuarios
function filterUsers() {
    const searchTerm = document.getElementById('userSearch')?.value.toLowerCase();
    const roleFilter = document.getElementById('roleFilter')?.value;
    const statusFilter = document.getElementById('statusFilter')?.value;
    
    const rows = document.querySelectorAll('#usersTable tbody tr');
    
    rows.forEach(row => {
        const name = row.cells[1]?.textContent.toLowerCase();
        const email = row.cells[2]?.textContent.toLowerCase();
        const role = row.cells[3]?.textContent.toLowerCase();
        const status = row.cells[4]?.textContent.toLowerCase();
        
        let show = true;
        
        // Filtro por búsqueda
        if (searchTerm && !name.includes(searchTerm) && !email.includes(searchTerm)) {
            show = false;
        }
        
        // Filtro por rol
        if (roleFilter && role !== roleFilter.toLowerCase()) {
            show = false;
        }
        
        // Filtro por estado
        if (statusFilter && status !== statusFilter.toLowerCase()) {
            show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

// Mostrar modal de agregar usuario
function showAddUserModal() {
    document.getElementById('userModalTitle').textContent = 'Agregar Usuario';
    document.getElementById('userForm').reset();
    currentEditingUser = null;
    showModal('userModal');
}

// Editar usuario
async function editUser(userId) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/usuarios/${userId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            currentEditingUser = user;
            
            // Llenar formulario con datos del usuario
            document.getElementById('userName').value = user.nombre;
            document.getElementById('userEmail').value = user.email;
            document.getElementById('userPhone').value = user.telefono || '';
            document.getElementById('userRole').value = user.rol;
            document.getElementById('userAddress').value = user.direccion || '';
            
            document.getElementById('userModalTitle').textContent = 'Editar Usuario';
            showModal('userModal');
        }
    } catch (error) {
        console.error('❌ Error cargando usuario:', error);
        showNotification('Error al cargar usuario', 'error');
    }
}

// Manejar envío del formulario de usuario
async function handleUserSubmit(e) {
    e.preventDefault();
    
    const formData = {
        nombre: document.getElementById('userName').value,
        email: document.getElementById('userEmail').value,
        telefono: document.getElementById('userPhone').value,
        rol: document.getElementById('userRole').value,
        direccion: document.getElementById('userAddress').value
    };
    
    // Solo incluir contraseña si se está creando un nuevo usuario
    const password = document.getElementById('userPassword').value;
    const passwordConfirm = document.getElementById('userPasswordConfirm').value;
    
    if (!currentEditingUser && password) {
        if (password !== passwordConfirm) {
        showNotification('Las contraseñas no coinciden', 'error');
        return;
    }
        formData.password = password;
    }
    
    try {
        const url = currentEditingUser 
            ? `${API_CONFIG.BASE_URL}/admin/usuarios/${currentEditingUser.id}`
            : `${API_CONFIG.BASE_URL}/admin/usuarios`;
        
        const method = currentEditingUser ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showNotification(
                currentEditingUser ? 'Usuario actualizado correctamente' : 'Usuario creado correctamente',
                'success'
            );
            closeModal('userModal');
            loadUsers();
            currentEditingUser = null;
        } else {
            throw new Error('Error al guardar usuario');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al guardar usuario', 'error');
    }
}

// Cambiar estado de usuario
async function toggleUserStatus(userId) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/usuarios/${userId}/toggle-status`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            showNotification('Estado de usuario actualizado', 'success');
            loadUsers();
        } else {
            throw new Error('Error al cambiar estado de usuario');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al cambiar estado de usuario', 'error');
    }
}

// ===== GESTIÓN DE PEDIDOS =====

// Cargar pedidos
async function loadOrders() {
    try {
        console.log('🛒 Cargando pedidos...');
        
        const token = localStorage.getItem('authToken');
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/pedidos`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const orders = await response.json();
            console.log('✅ Pedidos cargados:', orders);
            displayOrdersTable(orders);
        } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('❌ Error al cargar pedidos:', error);
        showNotification('Error al cargar pedidos', 'error');
    }
}

// Mostrar tabla de pedidos
function displayOrdersTable(orders) {
    const container = document.getElementById('ordersTable');
    if (!container) return;
    
    if (!orders || orders.length === 0) {
        container.innerHTML = '<p class="no-data">No hay pedidos disponibles</p>';
        return;
    }
    
    container.innerHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Número</th>
                    <th>Cliente</th>
                    <th>Total</th>
                    <th>Estado</th>
                    <th>Fecha</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${orders.map(order => `
                    <tr>
                        <td>${order.numero_pedido || order.id}</td>
                        <td>${order.cliente_nombre || 'N/A'}</td>
                        <td>$${(order.total || 0).toLocaleString()}</td>
                        <td>
                            <span class="status-badge ${order.estado?.toLowerCase()}">${order.estado || 'PENDIENTE'}</span>
                        </td>
                        <td>${new Date(order.fecha_creacion).toLocaleDateString('es-ES')}</td>
                        <td>
                            <div class="action-buttons">
                                <button onclick="viewOrderDetails(${order.id})" class="btn-view" title="Ver Detalles">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button onclick="updateOrderStatus(${order.id})" class="btn-edit" title="Actualizar Estado">
                                    <i class="fas fa-edit"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Filtrar pedidos
function filterOrders() {
    const searchTerm = document.getElementById('orderSearch')?.value.toLowerCase();
    const statusFilter = document.getElementById('orderStatusFilter')?.value;
    const dateFilter = document.getElementById('orderDateFilter')?.value;
    
    const rows = document.querySelectorAll('#ordersTable tbody tr');
    
    rows.forEach(row => {
        const orderNumber = row.cells[0]?.textContent.toLowerCase();
        const customer = row.cells[1]?.textContent.toLowerCase();
        const status = row.cells[3]?.textContent.toLowerCase();
        const date = row.cells[4]?.textContent;
        
        let show = true;
        
        // Filtro por búsqueda
        if (searchTerm && !orderNumber.includes(searchTerm) && !customer.includes(searchTerm)) {
            show = false;
        }
        
        // Filtro por estado
        if (statusFilter && status !== statusFilter.toLowerCase()) {
            show = false;
        }
        
        // Filtro por fecha
        if (dateFilter && date !== dateFilter) {
            show = false;
        }
        
        row.style.display = show ? '' : 'none';
    });
}

// Ver detalles del pedido
async function viewOrderDetails(orderId) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/pedidos/${orderId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const order = await response.json();
            currentOrderDetails = order;
            showOrderDetailsModal(order);
        }
    } catch (error) {
        console.error('❌ Error cargando detalles del pedido:', error);
        showNotification('Error al cargar detalles del pedido', 'error');
    }
}

// Mostrar modal de detalles del pedido
function showOrderDetailsModal(order) {
    const container = document.getElementById('orderDetailsContent');
    if (!container) return;
    
    container.innerHTML = `
        <div class="order-details">
            <h4>Pedido #${order.numero_pedido || order.id}</h4>
            <p><strong>Cliente:</strong> ${order.cliente_nombre || 'N/A'}</p>
            <p><strong>Estado:</strong> ${order.estado || 'PENDIENTE'}</p>
            <p><strong>Total:</strong> $${(order.total || 0).toLocaleString()}</p>
            <p><strong>Fecha:</strong> ${new Date(order.fecha_creacion).toLocaleDateString('es-ES')}</p>
            <p><strong>Método de pago:</strong> ${order.metodo_pago || 'N/A'}</p>
        </div>
    `;
    
    showModal('orderDetailsModal');
}

// Contactar cliente
async function contactCustomer(customerId) {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/usuarios/${customerId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const customer = await response.json();
            showContactModal(customer);
        }
    } catch (error) {
        console.error('❌ Error cargando datos del cliente:', error);
        showNotification('Error al cargar datos del cliente', 'error');
    }
}

// Mostrar modal de contacto
function showContactModal(customer) {
    const customerInfo = document.getElementById('customerInfo');
    customerInfo.innerHTML = `
        <div class="customer-details">
            <h4>Información del Cliente</h4>
            <p><strong>Nombre:</strong> ${customer.nombre}</p>
            <p><strong>Email:</strong> ${customer.email}</p>
            <p><strong>Teléfono:</strong> ${customer.telefono || 'No disponible'}</p>
            <p><strong>Dirección:</strong> ${customer.direccion || 'No disponible'}</p>
        </div>
    `;
    
    showModal('contactModal');
}

// Manejar envío del formulario de contacto
async function handleContactSubmit(e) {
    e.preventDefault();
    
    const formData = {
        asunto: document.getElementById('contactSubject').value,
        mensaje: document.getElementById('contactMessage').value,
        cliente_id: currentOrderDetails?.cliente_id
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/contactar-cliente`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showNotification('Mensaje enviado correctamente', 'success');
            closeModal('contactModal');
        } else {
            throw new Error('Error al enviar mensaje');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al enviar mensaje', 'error');
    }
}

// ===== REPORTES =====

// Cargar reportes
async function loadReports() {
    try {
        console.log('📊 Cargando reportes...');
        
        // Cargar gráficos
        await loadSalesChart();
        await loadTopProductsChart();
        await loadUsersChart();
        await loadOrdersChart();
        
    } catch (error) {
        console.error('❌ Error al cargar reportes:', error);
        showNotification('Error al cargar reportes', 'error');
    }
}

// Inicializar gráficos
function initializeCharts() {
    console.log('📈 Inicializando gráficos...');
    // Los gráficos se cargarán cuando se acceda a la sección de reportes
}

// Cargar gráfico de ventas
async function loadSalesChart() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/reportes/ventas`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            createSalesChart(data.ventas_por_dia || []);
        }
    } catch (error) {
        console.error('❌ Error cargando gráfico de ventas:', error);
    }
}

// Crear gráfico de ventas
function createSalesChart(data) {
    const ctx = document.getElementById('salesChart');
    if (!ctx) return;
    
    const labels = data.map(item => item.fecha);
    const values = data.map(item => item.total);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Ventas Diarias',
                data: values,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Cargar gráfico de productos más vendidos
async function loadTopProductsChart() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/reportes/ventas`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            createTopProductsChart(data.productos_mas_vendidos || []);
        }
    } catch (error) {
        console.error('❌ Error cargando gráfico de productos:', error);
    }
}

// Crear gráfico de productos más vendidos
function createTopProductsChart(data) {
    const ctx = document.getElementById('topProductsChart');
    if (!ctx) return;
    
    const labels = data.map(item => item.nombre);
    const values = data.map(item => item.cantidad_vendida);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cantidad Vendida',
                data: values,
                backgroundColor: 'rgba(54, 162, 235, 0.8)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Cargar gráfico de distribución de usuarios
async function loadUsersChart() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/usuarios`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const users = await response.json();
            createUsersChart(users);
        }
    } catch (error) {
        console.error('❌ Error cargando gráfico de usuarios:', error);
    }
}

// Crear gráfico de distribución de usuarios
function createUsersChart(users) {
    const ctx = document.getElementById('usersChart');
    if (!ctx) return;
    
    const roles = {};
    users.forEach(user => {
        roles[user.rol] = (roles[user.rol] || 0) + 1;
    });
    
    const labels = Object.keys(roles);
    const values = Object.values(roles);
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'];
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Cargar gráfico de estado de pedidos
async function loadOrdersChart() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/pedidos`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (response.ok) {
            const orders = await response.json();
            createOrdersChart(orders);
        }
    } catch (error) {
        console.error('❌ Error cargando gráfico de pedidos:', error);
    }
}

// Crear gráfico de estado de pedidos
function createOrdersChart(orders) {
    const ctx = document.getElementById('ordersChart');
    if (!ctx) return;
    
    const estados = {};
    orders.forEach(order => {
        const estado = order.estado || 'PENDIENTE';
        estados[estado] = (estados[estado] || 0) + 1;
    });
    
    const labels = Object.keys(estados);
    const values = Object.values(estados);
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length)
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Funciones auxiliares
function getStockLevel(stock) {
    if (stock <= 0) return 'out';
    if (stock <= 10) return 'low';
    if (stock <= 50) return 'medium';
    return 'high';
}

function getStockStatus(stock, stockMinimo) {
    if (stock <= 0) return 'out';
    if (stock <= stockMinimo) return 'low';
    return 'ok';
}

function getStockStatusText(stock, stockMinimo) {
    if (stock <= 0) return 'Agotado';
    if (stock <= stockMinimo) return 'Bajo Stock';
    return 'OK';
}

// ===== CONFIGURACIÓN =====

// Manejar configuración general
async function handleGeneralConfig(e) {
    e.preventDefault();
    
    const formData = {
        nombre_tienda: document.getElementById('storeName').value,
        email_contacto: document.getElementById('contactEmail').value,
        telefono_contacto: document.getElementById('contactPhone').value,
        direccion_tienda: document.getElementById('storeAddress').value
    };
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/admin/configuracion/general`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showNotification('Configuración actualizada correctamente', 'success');
        } else {
            throw new Error('Error al actualizar configuración');
        }
    } catch (error) {
        console.error('❌ Error:', error);
        showNotification('Error al actualizar configuración', 'error');
    }
}

// ===== UTILIDADES =====

// Mostrar modal
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
    }
}

// Cerrar modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Exportar pedidos
function exportOrders() {
    showNotification('Exportando pedidos...', 'info');
}

// Actualizar pedidos
function refreshOrders() {
    loadOrders();
    showNotification('Pedidos actualizados', 'success');
}

// Actualizar estado del pedido
function updateOrderStatus() {
    showNotification('Funcionalidad en desarrollo', 'info');
}

function generateReport(type) {
    showNotification(`Generando reporte de ${type}...`, 'info');
}

// Cerrar modales al hacer clic fuera
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
} 

// ===== INICIALIZACIÓN GLOBAL =====
// Asegurar que todas las funciones necesarias estén disponibles globalmente
window.logout = logout;
window.clearAuthData = clearAuthData;
window.showModal = showModal;
window.closeModal = closeModal;
window.showNotification = showNotification;
window.showAddProductModal = showAddProductModal;
window.showAddUserModal = showAddUserModal;
window.exportOrders = exportOrders;
window.refreshOrders = refreshOrders;
window.updateOrderStatus = updateOrderStatus;
window.generateReport = generateReport;

console.log('✅ Funciones globales del dashboard admin cargadas');

// Cargar datos simulados del dashboard (para desarrollo)
function loadSimulatedDashboardData() {
    console.log('🔧 Cargando datos simulados del dashboard...');
    
    // Estadísticas simuladas
    const simulatedStats = {
        total_usuarios: 150,
        total_pedidos: 89,
        total_productos: 45,
        ventas_hoy: 1250000
    };
    updateDashboardStats(simulatedStats);
    
    // Pedidos recientes simulados
    const simulatedOrders = [
        {
            id: 1,
            cliente: { nombre: 'Juan Pérez' },
            total: 45000,
            estado: 'pendiente',
            fecha: new Date().toISOString()
        },
        {
            id: 2,
            cliente: { nombre: 'María González' },
            total: 78000,
            estado: 'completado',
            fecha: new Date(Date.now() - 86400000).toISOString()
        }
    ];
    displayRecentOrders(simulatedOrders);
    
    // Productos con bajo stock simulados
    const simulatedLowStock = [
        {
            codigo: 'H001',
            nombre: 'Martillo Profesional',
            stock: 3,
            stock_minimo: 5
        },
        {
            codigo: 'T002',
            nombre: 'Taladro Eléctrico',
            stock: 1,
            stock_minimo: 3
        }
    ];
    displayLowStockProducts(simulatedLowStock);
    
    console.log('✅ Datos simulados cargados');
}

// =============================================================================
// FUNCIONES DE CHAT DE SOPORTE
// =============================================================================

// Cargar lista de chats
async function loadChats() {
    try {
        const response = await API.chat.listarChats();
        chatsList = response.chats || [];
        
        renderChatList();
        updateChatNotification();
        
        // Configurar auto-refresh cada 30 segundos
        if (!chatRefreshInterval) {
            chatRefreshInterval = setInterval(loadChats, 30000);
        }
        
    } catch (error) {
        console.error('Error al cargar chats:', error);
        showNotification('Error al cargar chats', 'error');
    }
}

// Renderizar lista de chats
function renderChatList() {
    const chatList = document.getElementById('chatList');
    const totalChats = document.getElementById('totalChats');
    
    if (!chatList) return;
    
    totalChats.textContent = `${chatsList.length} chats`;
    
    if (chatsList.length === 0) {
        chatList.innerHTML = '<div class="no-chats">No hay chats activos</div>';
        return;
    }
    
    chatList.innerHTML = chatsList.map(chat => {
        const isUnread = !chat.leido_admin;
        const isActive = chat.id === currentChatId;
        const timeAgo = getTimeAgo(chat.fecha_ultima_actividad);
        
        return `
            <div class="chat-item ${isActive ? 'active' : ''} ${isUnread ? 'unread' : ''}" 
                 onclick="selectChat(${chat.id})">
                <div class="chat-item-header">
                    <h4>${chat.cliente_nombre || 'Cliente'}</h4>
                    <span class="chat-time">${timeAgo}</span>
                </div>
                <div class="chat-item-content">
                    <p class="chat-preview">${chat.asunto || 'Consulta de soporte'}</p>
                    <span class="chat-status-badge ${chat.estado}">${getEstadoText(chat.estado)}</span>
                </div>
                ${isUnread ? '<div class="unread-indicator"></div>' : ''}
            </div>
        `;
    }).join('');
}

// Seleccionar un chat
async function selectChat(chatId) {
    currentChatId = chatId;
    
    // Actualizar UI
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const selectedItem = document.querySelector(`[onclick="selectChat(${chatId})"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }
    
    // Mostrar área de mensajes
    document.getElementById('chatMessagesHeader').style.display = 'flex';
    document.getElementById('chatMessagesContainer').style.display = 'flex';
    document.getElementById('noChatSelected').style.display = 'none';
    
    // Cargar mensajes del chat
    await loadChatMessages(chatId);
    
    // Marcar como leído
    try {
        await API.chat.marcarLeido(chatId);
        loadChats(); // Recargar lista para actualizar indicadores
    } catch (error) {
        console.error('Error al marcar como leído:', error);
    }
}

// Cargar mensajes de un chat específico
async function loadChatMessages(chatId) {
    try {
        const mensajes = await API.chat.obtenerMensajesChat(chatId);
        renderChatMessages(mensajes);
        
        // Actualizar información del chat
        const chat = chatsList.find(c => c.id === chatId);
        if (chat) {
            document.getElementById('currentChatTitle').textContent = 
                `Chat #${chatId} - ${chat.cliente_nombre || 'Cliente'}`;
            document.getElementById('currentChatStatus').textContent = getEstadoText(chat.estado);
            document.getElementById('currentChatStatus').className = `chat-status ${chat.estado}`;
            document.getElementById('chatStateSelect').value = chat.estado;
        }
        
    } catch (error) {
        console.error('Error al cargar mensajes:', error);
        showNotification('Error al cargar mensajes', 'error');
    }
}

// Renderizar mensajes del chat
function renderChatMessages(mensajes) {
    const chatMessages = document.getElementById('chatMessages');
    
    if (!chatMessages) return;
    
    chatMessages.innerHTML = mensajes.map(mensaje => {
        const isUser = mensaje.tipo === 'usuario';
        const isBot = mensaje.tipo === 'bot';
        const isAdmin = mensaje.tipo === 'admin';
        
        let messageClass = 'message';
        if (isUser) messageClass += ' user';
        if (isBot) messageClass += ' system';
        if (isAdmin) messageClass += ' admin';
        
        const time = new Date(mensaje.fecha_envio).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <div class="${messageClass}">
                <div class="message-content">
                    <p>${mensaje.contenido}</p>
                    <span class="message-time">${time}</span>
                </div>
            </div>
        `;
    }).join('');
    
    // Scroll al final
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Enviar mensaje como admin
async function sendAdminMessage() {
    const input = document.getElementById('adminChatInput');
    const message = input.value.trim();
    
    if (!message || !currentChatId) return;
    
    try {
        await API.chat.responderChat(currentChatId, message);
        input.value = '';
        
        // Recargar mensajes
        await loadChatMessages(currentChatId);
        
        // Recargar lista de chats para actualizar última actividad
        loadChats();
        
    } catch (error) {
        console.error('Error al enviar mensaje:', error);
        showNotification('Error al enviar mensaje', 'error');
    }
}

// Cambiar estado del chat
async function changeChatState() {
    if (!currentChatId) return;
    
    const newState = document.getElementById('chatStateSelect').value;
    
    try {
        await API.chat.cambiarEstado(currentChatId, newState);
        showNotification(`Estado cambiado a ${getEstadoText(newState)}`, 'success');
        
        // Recargar lista de chats
        loadChats();
        
    } catch (error) {
        console.error('Error al cambiar estado:', error);
        showNotification('Error al cambiar estado', 'error');
    }
}

// Marcar chat como leído
async function markChatAsRead() {
    if (!currentChatId) return;
    
    try {
        await API.chat.marcarLeido(currentChatId);
        showNotification('Chat marcado como leído', 'success');
        loadChats(); // Recargar lista
        
    } catch (error) {
        console.error('Error al marcar como leído:', error);
        showNotification('Error al marcar como leído', 'error');
    }
}

// Filtrar chats por estado
function filterChats() {
    const filter = document.getElementById('chatStatusFilter').value;
    
    if (!filter) {
        renderChatList();
        return;
    }
    
    const filteredChats = chatsList.filter(chat => chat.estado === filter);
    const chatList = document.getElementById('chatList');
    const totalChats = document.getElementById('totalChats');
    
    totalChats.textContent = `${filteredChats.length} chats`;
    
    if (filteredChats.length === 0) {
        chatList.innerHTML = '<div class="no-chats">No hay chats con este estado</div>';
        return;
    }
    
    chatList.innerHTML = filteredChats.map(chat => {
        const isUnread = !chat.leido_admin;
        const isActive = chat.id === currentChatId;
        const timeAgo = getTimeAgo(chat.fecha_ultima_actividad);
        
        return `
            <div class="chat-item ${isActive ? 'active' : ''} ${isUnread ? 'unread' : ''}" 
                 onclick="selectChat(${chat.id})">
                <div class="chat-item-header">
                    <h4>${chat.cliente_nombre || 'Cliente'}</h4>
                    <span class="chat-time">${timeAgo}</span>
                </div>
                <div class="chat-item-content">
                    <p class="chat-preview">${chat.asunto || 'Consulta de soporte'}</p>
                    <span class="chat-status-badge ${chat.estado}">${getEstadoText(chat.estado)}</span>
                </div>
                ${isUnread ? '<div class="unread-indicator"></div>' : ''}
            </div>
        `;
    }).join('');
}

// Actualizar notificación de chat
function updateChatNotification() {
    const notification = document.getElementById('chat-notification');
    const unreadCount = chatsList.filter(chat => !chat.leido_admin).length;
    
    if (unreadCount > 0) {
        notification.textContent = unreadCount;
        notification.style.display = 'inline';
    } else {
        notification.style.display = 'none';
    }
}

// Refrescar chats
function refreshChats() {
    loadChats();
    showNotification('Chats actualizados', 'success');
}

// Funciones auxiliares
function getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Ahora';
    if (diffMins < 60) return `${diffMins}m`;
    if (diffHours < 24) return `${diffHours}h`;
    return `${diffDays}d`;
}

function getEstadoText(estado) {
    const estados = {
        'abierto': 'Abierto',
        'en_proceso': 'En Proceso',
        'cerrado': 'Cerrado'
    };
    return estados[estado] || estado;
}

// Event listeners para el chat
document.addEventListener('DOMContentLoaded', function() {
    const adminChatInput = document.getElementById('adminChatInput');
    if (adminChatInput) {
        adminChatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendAdminMessage();
            }
        });
    }
    
    // Cargar chats al iniciar
    loadChats();
}); 