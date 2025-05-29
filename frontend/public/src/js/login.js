document.getElementById("loginForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();
  const message = document.getElementById("message");

  message.textContent = "";
  message.style.color = "black";

  if (!email || !password) {
    message.textContent = "Por favor, completa todos los campos.";
    message.style.color = "red";
    return;
  }

  try {
    message.textContent = "Verificando credenciales...";
    message.style.color = "blue";

    const loginRes = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ email, password }),  // Verifica si backend usa email o username
    });

    if (loginRes.ok) {
      const data = await loginRes.json();
      console.log("Login exitoso:", data);

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("rol", data.rol);
      localStorage.setItem("username", data.usuario);

      message.textContent = "¡Login exitoso! Redirigiendo...";
      message.style.color = "green";

      setTimeout(() => {
        if (data.rol === "empleado") {
          window.location.href = "/dashboard"; 
        } else {
          window.location.href = "/dashboard"; 
        }
      }, 1000);
      return;
    }

    if (loginRes.status === 401) {
      message.textContent = "Usuario no encontrado. Creando cuenta automáticamente...";
      message.style.color = "orange";

      const createRes = await fetch("http://localhost:8000/usuarios/", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify({ 
          email,
          password,
          username: email.split('@')[0],  // Asegúrate que tu backend acepta username
          rol: "cliente" 
        }),
      });

      if (createRes.ok) {
        message.textContent = "Cuenta creada exitosamente. Iniciando sesión...";
        message.style.color = "green";

        setTimeout(async () => {
          try {
            const secondLoginRes = await fetch("http://localhost:8000/login", {
              method: "POST",
              headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
              },
              body: JSON.stringify({ email, password }),
            });

            if (secondLoginRes.ok) {
              const data = await secondLoginRes.json();
              console.log("Segundo login exitoso:", data);

              localStorage.setItem("token", data.access_token);
              localStorage.setItem("rol", data.rol);
              localStorage.setItem("username", data.usuario);

              message.textContent = "¡Bienvenido! Redirigiendo al dashboard...";
              message.style.color = "green";

              setTimeout(() => {
                window.location.href = "/dashboard";
              }, 1000);
            } else {
              const errorData = await secondLoginRes.json();
              message.textContent = errorData.detail || "Error al iniciar sesión después de crear la cuenta.";
              message.style.color = "red";
            }
          } catch (err) {
            console.error("Error en segundo login:", err);
            message.textContent = "Error al iniciar sesión después de crear la cuenta.";
            message.style.color = "red";
          }
        }, 2000);
      } else {
        const createError = await createRes.json();
        console.error("Error al crear usuario:", createError);
        message.textContent = createError.detail || "Error al crear la cuenta automáticamente.";
        message.style.color = "red";
      }
    } else {
      const loginError = await loginRes.json();
      console.error("Error de login:", loginError);
      message.textContent = loginError.detail || "Error en las credenciales.";
      message.style.color = "red";
    }
  } catch (err) {
    console.error("Error de conexión:", err);
    message.textContent = "Error al conectar con el servidor. Verifica que esté ejecutándose.";
    message.style.color = "red";
  }
});
