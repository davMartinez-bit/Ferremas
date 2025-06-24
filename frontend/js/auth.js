// Sistema de Autenticación Compartido - Ferremas

// Verificar que API_CONFIG esté disponible
if (typeof API_CONFIG === 'undefined') {
    console.error('❌ API_CONFIG no está definido. Asegúrate de que config.js se cargue antes que auth.js');
    // Definir una configuración por defecto como fallback
    window.API_CONFIG = {
        BASE_URL: 'http://localhost:8000/api'
    };
}

// Limpiar localStorage al cargar la página (evitar sesiones fantasma)
document.addEventListener('DOMContentLoaded', function() {
    // Solo limpiar si estamos en la página de login específicamente
    if (window.location.pathname.includes('login.html') || window.location.pathname === '/login') {
        console.log('🧹 Limpiando localStorage en página de login...');
        clearAuthData();
    }
});

// Función para manejar el login
async function handleLogin(email, password) {
    try {
        console.log('🔐 Iniciando login con credenciales reales...');
        
        const response = await fetch(`${API_CONFIG.BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ username: email, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Login exitoso:', data.user.rol);
            
            // Guardar token y datos del usuario (TOKEN REAL)
            localStorage.setItem('authToken', data.access_token);
            localStorage.setItem('userData', JSON.stringify(data.user));
            localStorage.setItem('rol', data.user.rol);
            
            showNotification(`Inicio de sesión exitoso como ${data.user.rol}`, 'success');
            
            // Redirigir según el rol
            setTimeout(() => {
                if (data.user.rol === 'cliente') {
                    window.location.href = '/html/clientedashboard.html';
                } else if (data.user.rol === 'empleado' || data.user.rol === 'admin') {
                    window.location.href = '/html/emp_dashboard.html';
                } else {
                    window.location.href = '/dashboard';
                }
            }, 1500);
        } else {
            const error = await response.json();
            console.error('❌ Error en login:', error);
            showNotification(error.detail || 'Error en las credenciales', 'error');
        }
    } catch (error) {
        console.error('❌ Error de conexión en login:', error);
        showNotification('Error al conectar con el servidor', 'error');
    }
}

// Función para manejar el logout
function handleLogout() {
    console.log('🚪 Cerrando sesión...');
    
    // Limpiar datos de autenticación
    clearAuthData();
    
    showNotification('Sesión cerrada exitosamente', 'success');
    
    // Redirigir a la página principal
    setTimeout(() => {
        window.location.href = '/';
    }, 1500);
}

// Verificar estado de autenticación
async function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (!token || !userData) {
        console.log('❌ No hay token o userData');
        return null;
    }
    
    // Validar token con el servidor (SIEMPRE)
    try {
        console.log('🔍 Validando token con el servidor...');
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
            return user;
        } else {
            console.log('❌ Token inválido o expirado');
            clearAuthData();
            return null;
        }
    } catch (error) {
        console.error('❌ Error al validar token:', error);
        clearAuthData();
        return null;
    }
}

// Verificar estado de autenticación (versión síncrona para compatibilidad)
function checkAuthStatusSync() {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (token && userData) {
        try {
            return JSON.parse(userData);
        } catch (error) {
            console.error('❌ Error al parsear datos del usuario:', error);
            clearAuthData();
            return null;
        }
    }
    return null;
}

// Limpiar datos de autenticación
function clearAuthData() {
    console.log('🧹 Limpiando datos de autenticación...');
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    localStorage.removeItem('rol');
    console.log('✅ Datos de autenticación limpiados');
}

// Mostrar notificación
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
            document.body.removeChild(notification);
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

// Función para verificar token válido (usada en dashboards)
async function checkTokenValidity() {
    const token = localStorage.getItem('authToken');
    if (!token) {
        console.log('❌ No hay token');
        return false;
    }
    
    // Verificar si es un token simulado (para desarrollo)
    if (token.includes('mock-')) {
        console.log('🔧 Token simulado detectado, permitiendo acceso...');
        return true;
    }
    
    try {
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
        console.error('❌ Error al verificar token:', error);
        return false;
    }
}

// ===== FUNCIONES DE DESARROLLO (SOLO PARA TESTING) =====

// Función para simular login de administrador (para desarrollo)
function simulateAdminLogin() {
    console.log('🔧 Simulando login de administrador para desarrollo...');
    
    const mockAdmin = {
        id: 1,
        nombre: 'Administrador Demo',
        email: 'admin@ferremas.com',
        rol: 'admin',
        token: 'mock-admin-token-12345'
    };
    
    localStorage.setItem('authToken', mockAdmin.token);
    localStorage.setItem('userData', JSON.stringify(mockAdmin));
    localStorage.setItem('rol', mockAdmin.rol);
    
    showNotification('Inicio de sesión como administrador (Demo)', 'success');
    
    setTimeout(() => {
        window.location.href = '/html/emp_dashboard.html';
    }, 1500);
}

// Función para simular login de cliente (para desarrollo)
function simulateClientLogin() {
    console.log('🔧 Simulando login de cliente para desarrollo...');
    
    const mockClient = {
        id: 2,
        nombre: 'Cliente Demo',
        email: 'cliente@demo.com',
        rol: 'cliente',
        token: 'mock-client-token-12345'
    };
    
    localStorage.setItem('authToken', mockClient.token);
    localStorage.setItem('userData', JSON.stringify(mockClient));
    localStorage.setItem('rol', mockClient.rol);
    
    showNotification('Inicio de sesión como cliente (Demo)', 'success');
    
    setTimeout(() => {
        window.location.href = '/html/clientedashboard.html';
    }, 1500);
} 
