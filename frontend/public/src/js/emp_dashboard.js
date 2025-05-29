document.addEventListener("DOMContentLoaded", () => {
  const rol = localStorage.getItem("rol");
  const username = localStorage.getItem("username");

  if (!rol || rol !== "empleado") {
    window.location.href = "login.html";
    return;
  }

  document.getElementById("usernameDisplay").textContent = `Bienvenido: ${username}`;
});

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("rol");
  localStorage.removeItem("username");
  window.location.href = "login.html";
}

async function loadSection(section) {
  try {
    const token = localStorage.getItem("token");
    const response = await fetch(`http://localhost:8000/api/${section}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error("Error al cargar la sección");
    }

    const data = await response.json();
    // Aquí procesarías los datos y actualizarías el DOM
    document.getElementById("contentSection").innerHTML = `
      <h2>${section.charAt(0).toUpperCase() + section.slice(1)}</h2>
      <pre>${JSON.stringify(data, null, 2)}</pre>
    `;
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("contentSection").innerHTML = `
      <h2>Error</h2>
      <p>No se pudo cargar la sección: ${error.message}</p>
    `;
  }
}