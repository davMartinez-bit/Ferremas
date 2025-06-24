// Script principal de la aplicación - Ferremas

let currentUser = null;

// Función principal que se ejecuta al cargar la página
async function initializeApp() {
    console.log('🚀 Inicializando aplicación...');
    
    // Verificar estado de autenticación
    await checkUserAuthStatus();
    
    // Configurar carrito
    setupCart();
    
    // Verificar estado del pago (después de verificar autenticación)
    await checkPaymentStatus();
    
    console.log('✅ Aplicación inicializada');
}

// Ejecutar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', initializeApp);

// Verificar estado de autenticación
async function checkUserAuthStatus() {
    console.log('🔍 checkUserAuthStatus (main.js) iniciado...');
    
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (!token || !userData) {
        console.log('❌ No hay token o userData, usuario no autenticado');
        currentUser = null;
        updateAuthUI();
        return;
    }
    
    // Verificar token con el servidor
    try {
        const isValid = await checkTokenValidity();
        if (!isValid) {
            console.log('❌ Token inválido, limpiando datos...');
            clearAuthData();
            currentUser = null;
            updateAuthUI();
            return;
        }
        
        // Intentar parsear los datos del usuario
        const parsedUser = JSON.parse(userData);
        console.log('✅ userData parseado correctamente:', parsedUser.nombre);
        
        // Verificar que el usuario tiene los campos mínimos necesarios
        if (!parsedUser.id || !parsedUser.email || !parsedUser.rol) {
            console.log('⚠️ userData incompleto, limpiando datos...');
            clearAuthData();
            currentUser = null;
            updateAuthUI();
            return;
        }
        
        // Usar los datos del localStorage directamente
        currentUser = parsedUser;
        console.log('✅ Usuario autenticado:', currentUser.nombre, `(${currentUser.rol})`);
        
    } catch (error) {
        console.error('❌ Error al verificar autenticación:', error);
        clearAuthData();
        currentUser = null;
    }
    
    console.log('🎯 checkUserAuthStatus (main.js) completado. currentUser:', currentUser ? currentUser.nombre : 'null');
    updateAuthUI();
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

// Actualizar interfaz según estado de autenticación
function updateAuthUI() {
    const authLinks = document.getElementById('auth-links');
    const userInfo = document.getElementById('user-info');
    const userName = document.getElementById('user-name');
    
    if (currentUser) {
        // Usuario autenticado
        userName.textContent = currentUser.nombre;
        userInfo.style.display = 'flex';
        
        // Mostrar enlace al dashboard según el rol
        let dashboardHref = '/html/clientedashboard.html';
        if (currentUser.rol === 'empleado' || currentUser.rol === 'admin') {
                    dashboardHref = '/html/emp_dashboard.html';
        }
        
        authLinks.innerHTML = `
            <a href="${dashboardHref}" class="nav-link">
                <i class="fas fa-user"></i> Mi Cuenta
            </a>
        `;
    } else {
        // Usuario no autenticado
        userInfo.style.display = 'none';
        authLinks.innerHTML = `
            <a href="/login" class="nav-link">
                <i class="fas fa-sign-in-alt"></i> Iniciar Sesión
            </a>
        `;
    }

    // Reemplazar todos los enlaces a /dashboard por el dashboardHref correcto
    document.querySelectorAll('a[href="/dashboard"]').forEach(a => a.href = dashboardHref);
}

// Configurar carrito
function setupCart() {
    const toggleCartBtn = document.getElementById('toggle-cart');
    const cartCount = document.getElementById('cart-count');
    
    if (toggleCartBtn && cartCount) {
        // Cargar carrito guardado
    const savedCart = localStorage.getItem('carrito');
    if (savedCart) {
            try {
                const cart = JSON.parse(savedCart);
                cartCount.textContent = cart.length || 0;
            } catch (error) {
                console.error('Error al cargar carrito:', error);
                cartCount.textContent = '0';
            }
        }
        
        // Event listener para mostrar carrito
        toggleCartBtn.addEventListener('click', function() {
            window.location.href = '/productos.html#carrito';
        });
    }
}

// Verificar estado del pago desde parámetros de URL
async function checkPaymentStatus() {
    const urlParams = new URLSearchParams(window.location.search);
    const pagoStatus = urlParams.get('pago');
    
    if (pagoStatus) {
        console.log('💰 Estado de pago detectado:', pagoStatus);
        
        if (pagoStatus === 'exitoso') {
            const pedidoId = urlParams.get('pedido_id');
            const tempToken = urlParams.get('temp_token');
            
            showNotification(`¡Pago exitoso! Tu pedido #${pedidoId} ha sido confirmado.`, 'success');
            
            // Si hay token temporal, restaurar la sesión
            if (tempToken) {
                console.log('🔑 Token temporal detectado, restaurando sesión...');
                try {
                    // Guardar el token temporal
                    localStorage.setItem('authToken', tempToken);
                    
                    // Obtener información del usuario
                    const response = await fetch(`${API_CONFIG.BASE_URL}/usuarios/me`, {
                        headers: {
                            'Authorization': `Bearer ${tempToken}`
                        }
                    });
                    
                    if (response.ok) {
                        const user = await response.json();
                        localStorage.setItem('userData', JSON.stringify(user));
                        localStorage.setItem('rol', user.rol);
                        currentUser = user;
                        
                        console.log('✅ Sesión restaurada:', currentUser.nombre, `(${currentUser.rol})`);
                        
                        // Actualizar UI
                        updateAuthUI();
                        
                        // Redirigir al dashboard después de 3 segundos
                        setTimeout(() => {
                            if (currentUser.rol === 'cliente') {
                                window.location.href = '/html/clientedashboard.html';
                            } else {
                                window.location.href = '/html/emp_dashboard.html';
                            }
                        }, 3000);
                    } else {
                        console.log('⚠️ Error al restaurar sesión, redirigiendo a login...');
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 3000);
                    }
                } catch (error) {
                    console.error('❌ Error al restaurar sesión:', error);
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 3000);
                }
            } else {
                // Verificar si el usuario está autenticado
                if (currentUser) {
                    console.log('✅ Usuario autenticado, redirigiendo al dashboard...');
                    setTimeout(() => {
                        if (currentUser.rol === 'cliente') {
                            window.location.href = '/html/clientedashboard.html';
                        } else {
                            window.location.href = '/html/emp_dashboard.html';
                        }
                    }, 3000);
                } else {
                    console.log('⚠️ Usuario no autenticado, mostrando mensaje de éxito sin redirección');
                    showNotification('Pago exitoso. Inicia sesión para ver tu pedido.', 'success');
                }
            }
            
        } else if (pagoStatus === 'rechazado') {
            showNotification('El pago fue rechazado. Por favor, intenta nuevamente.', 'error');
            
        } else if (pagoStatus === 'error') {
            const mensaje = urlParams.get('mensaje');
            let errorMsg = 'Error en el proceso de pago.';
            
            if (mensaje === 'pago_no_encontrado') {
                errorMsg = 'No se encontró el pago. Contacta soporte.';
            } else if (mensaje === 'usuario_no_encontrado') {
                errorMsg = 'Error con la cuenta de usuario. Contacta soporte.';
            }
            
            showNotification(errorMsg, 'error');
        }
        
        // Limpiar parámetros de URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// Función de logout
function logout() {
    handleLogout();
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
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : type === 'warning' ? '#ffc107' : '#17a2b8'};
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        max-width: 300px;
        word-wrap: break-word;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
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
    
    // Remover después de 5 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
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
