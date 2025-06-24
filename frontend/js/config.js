// Configuración de la API - Ferremas Frontend
// Versión: 1.1 - Corregido manejo de errores 401

// Configuración base
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000/api',
    TIMEOUT: 10000, // 10 segundos
    RETRY_ATTEMPTS: 3
};

// Headers por defecto
const DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
};

// Función para obtener headers con autenticación
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
        ...DEFAULT_HEADERS,
        ...(token && { 'Authorization': `Bearer ${token}` })
    };
}

// Función para hacer peticiones HTTP
async function apiRequest(endpoint, options = {}) {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    const config = {
        headers: getAuthHeaders(),
        timeout: API_CONFIG.TIMEOUT,
        ...options
    };

    try {
        const response = await fetch(url, config);
        
        // Manejar diferentes códigos de respuesta
        if (response.ok) {
            return await response.json();
        } else if (response.status === 401) {
            // Token expirado o inválido - no redirigir automáticamente
            // Dejar que el código que llama a esta función decida qué hacer
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'No autorizado');
        } else if (response.status === 403) {
            throw new Error('No tienes permisos para esta acción');
        } else if (response.status === 404) {
            throw new Error('Recurso no encontrado');
        } else if (response.status >= 500) {
            throw new Error('Error del servidor');
        } else {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Error ${response.status}`);
        }
    } catch (error) {
        console.error('Error en API request:', error);
        throw error;
    }
}

// Funciones específicas de la API
const API = {
    // Autenticación
    auth: {
        login: (credentials) => apiRequest('/usuarios/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        }),
        register: (userData) => apiRequest('/usuarios/', {
            method: 'POST',
            body: JSON.stringify(userData)
        }),
        checkEmail: (email) => apiRequest(`/usuarios/check/${email}`),
        updateProfile: (profileData) => apiRequest('/usuarios/perfil', {
            method: 'PUT',
            body: JSON.stringify(profileData)
        }),
        changePassword: (passwordData) => apiRequest('/usuarios/password', {
            method: 'PUT',
            body: JSON.stringify(passwordData)
        }),
        getProfile: () => apiRequest('/usuarios/perfil')
    },

    // Productos
    productos: {
        getAll: (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            return apiRequest(`/productos/?${queryString}`);
        },
        getById: (id) => apiRequest(`/productos/${id}`),
        search: (query) => apiRequest(`/productos/buscar?q=${encodeURIComponent(query)}`),
        getByCategory: (categoryId) => apiRequest(`/productos/categoria/${categoryId}`),
        getDestacados: () => apiRequest('/productos/destacados'),
        getPromociones: () => apiRequest('/productos/promociones')
    },

    // Carrito
    carrito: {
        getAll: () => apiRequest('/carrito/'),
        get: () => apiRequest('/carrito/'), // Alias para compatibilidad
        add: (item) => apiRequest('/carrito/agregar', {
            method: 'POST',
            body: JSON.stringify(item)
        }),
        update: (itemId, item) => apiRequest(`/carrito/actualizar/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify(item)
        }),
        remove: (itemId) => apiRequest(`/carrito/eliminar/${itemId}`, {
            method: 'DELETE'
        }),
        clear: () => apiRequest('/carrito/limpiar', {
            method: 'DELETE'
        })
    },

    // Pedidos
    pedidos: {
        getAll: () => apiRequest('/pedidos/'),
        getById: (id) => apiRequest(`/pedidos/${id}`),
        create: (pedidoData) => apiRequest('/pedidos/crear', {
            method: 'POST',
            body: JSON.stringify(pedidoData)
        }),
        updateStatus: (id, status) => apiRequest(`/pedidos/${id}/estado`, {
            method: 'PUT',
            body: JSON.stringify({ estado: status })
        }),
        getItems: (id) => apiRequest(`/pedidos/${id}/items`)
    },

    // Mensajes
    mensajes: {
        getAll: (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            return apiRequest(`/mensajes/?${queryString}`);
        },
        getById: (id) => apiRequest(`/mensajes/${id}`),
        send: (mensajeData) => apiRequest('/mensajes/enviar', {
            method: 'POST',
            body: JSON.stringify(mensajeData)
        }),
        markAsRead: (id) => apiRequest(`/mensajes/${id}/leer`, {
            method: 'PUT'
        }),
        respond: (id, respuesta) => apiRequest(`/mensajes/${id}/responder`, {
            method: 'PUT',
            body: JSON.stringify(respuesta)
        }),
        getUnreadCount: () => apiRequest('/mensajes/no-leidos/count')
    },

    // Admin (solo para administradores)
    admin: {
        getStats: () => apiRequest('/admin/stats'),
        getAllPedidos: (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            return apiRequest(`/admin/pedidos?${queryString}`);
        },
        getAllUsuarios: (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            return apiRequest(`/admin/usuarios?${queryString}`);
        },
        getReportes: (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            return apiRequest(`/admin/reportes/ventas?${queryString}`);
        },
        updatePedidoStatus: (id, status) => apiRequest(`/admin/pedidos/${id}/estado?estado=${status}`, {
            method: 'PUT'
        })
    },

    // Pagos
    pagos: {
        create: (pagoData) => apiRequest('/pagos/crear', {
            method: 'POST',
            body: JSON.stringify(pagoData)
        }),
        createWebpayTransaction: () => apiRequest('/pagos/crear-transaccion-webpay', {
            method: 'POST'
        }),
        getById: (id) => apiRequest(`/pagos/${id}`),
        confirm: (id) => apiRequest(`/pagos/${id}/confirmar`, {
            method: 'POST'
        })
    },

    // Divisas
    divisas: {
        getCurrent: () => apiRequest('/divisas/actual'),
        getHistory: (days = 30) => apiRequest(`/divisas/historico?dias=${days}`),
        getAll: () => apiRequest('/divisas/'),
        getByCurrency: (moneda) => apiRequest(`/divisas/${moneda}`),
        convert: (moneda, monto, fecha = null) => {
            const params = new URLSearchParams({ monto });
            if (fecha) params.append('fecha', fecha);
            return apiRequest(`/divisas/convertir/${moneda}?${params.toString()}`);
        }
    },

    // Favoritos
    favoritos: {
        getAll: () => apiRequest('/favoritos/'),
        add: (productoId) => apiRequest('/favoritos/', {
            method: 'POST',
            body: JSON.stringify({ producto_id: productoId })
        }),
        remove: (productoId) => apiRequest(`/favoritos/${productoId}`, {
            method: 'DELETE'
        }),
        toggle: (productoId) => apiRequest(`/favoritos/toggle/${productoId}`, {
            method: 'POST'
        })
    },

    // Chat de Soporte
    chat: {
        iniciar: (asunto) => apiRequest('/chat/iniciar', {
            method: 'POST',
            body: JSON.stringify({ asunto })
        }),
        obtenerMiChat: () => apiRequest('/chat/mi-chat'),
        obtenerMensajes: () => apiRequest('/chat/mi-chat/mensajes'),
        enviarMensaje: (contenido) => apiRequest('/chat/enviar-mensaje', {
            method: 'POST',
            body: JSON.stringify({ contenido })
        }),
        // Endpoints para admin
        listarChats: (params = {}) => {
            const queryString = new URLSearchParams(params).toString();
            return apiRequest(`/chat/admin/chats?${queryString}`);
        },
        obtenerChat: (chatId) => apiRequest(`/chat/admin/chats/${chatId}`),
        obtenerMensajesChat: (chatId) => apiRequest(`/chat/admin/chats/${chatId}/mensajes`),
        responderChat: (chatId, contenido) => apiRequest(`/chat/admin/chats/${chatId}/responder`, {
            method: 'POST',
            body: JSON.stringify({ contenido })
        }),
        cambiarEstado: (chatId, estado) => apiRequest(`/chat/admin/chats/${chatId}/estado?estado=${estado}`, {
            method: 'PUT'
        }),
        marcarLeido: (chatId) => apiRequest(`/chat/admin/chats/${chatId}/marcar-leido`, {
            method: 'PUT'
        })
    }
};

// Función para manejar errores de red
function handleNetworkError(error) {
    console.error('Error de red:', error);
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        showNotification('Error de conexión. Verifica que el servidor esté ejecutándose.', 'error');
    } else {
        showNotification(error.message || 'Error desconocido', 'error');
    }
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Mostrar con animación
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Obtener icono para notificación
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

// Exportar para uso global
window.API = API;
window.API_CONFIG = API_CONFIG;
window.showNotification = showNotification;
window.handleNetworkError = handleNetworkError; 