document.getElementById("loginForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const message = document.getElementById("message");

  try {
    const res = await fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    if (!res.ok) {
      message.textContent = "Credenciales inválidas.";
      return;
    }

    const data = await res.json();
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("rol", data.role);

    // Redirige al usuario dependiendo del rol
    if (data.role === "empleado") {
      window.location.href = "dashboard_empleado.html";
    } else if (data.role === "cliente") {
      window.location.href = "dashboard_cliente.html";
    } else {
      message.textContent = "Rol no autorizado.";
    }

  } catch (err) {
    console.error(err);
    message.textContent = "Error al conectar con el servidor.";
  }
});

