// Lógica de login para Ferremas

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const message = document.getElementById('message');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const username = document.getElementById('username')?.value?.trim() || document.getElementById('email')?.value?.trim();
            const password = document.getElementById('password').value.trim();
            if (message) message.textContent = '';

            try {
                const response = await fetch('http://localhost:8000/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                if (!response.ok) {
                    const data = await response.json().catch(() => ({}));
                    if (message) message.textContent = data.detail || 'Error de autenticación';
                    return;
                }

                const data = await response.json();
                // Guardar token y rol en localStorage
                localStorage.setItem('authToken', data.access_token);
                localStorage.setItem('rol', data.user.rol);
                localStorage.setItem('userData', JSON.stringify(data.user));

                // Redirigir según el rol
                if (data.user.rol === 'cliente') {
                    window.location.href = '/html/clientedashboard.html';
                } else if (data.user.rol === 'empleado' || data.user.rol === 'admin') {
                    window.location.href = '/html/emp_dashboard.html';
                } else {
                    if (message) message.textContent = 'Rol no reconocido';
                }
            } catch (err) {
                if (message) message.textContent = 'Error de red o del servidor';
            }
        });
    }
}); 