document.addEventListener("DOMContentLoaded", async () => {
  // Verificar autenticación al cargar la página
  const user = await checkUserAuthStatus();
  if (!user) {
    window.location.href = "/login";
    return;
  }

  const rol = localStorage.getItem("rol");
  const mensaje = document.getElementById("mensaje");

  document.getElementById("rolInfo").textContent = `Rol actual: ${rol ? rol.toUpperCase() : ''}`;

  if (rol === "cliente") {
    document.getElementById("btnPut").style.display = "none";
    document.getElementById("btnDelete").style.display = "none";
  }
});

function logout() {
  localStorage.removeItem("authToken");
  localStorage.removeItem("userData");
  localStorage.removeItem("rol");
  window.location.href = "/login";
}

function simularGet() {
  document.getElementById("mensaje").textContent = "GET: Productos simulados cargados correctamente.";
}

function simularPut() {
  document.getElementById("mensaje").textContent = "PUT: Producto actualizado (simulado).";
}

function simularDelete() {
  document.getElementById("mensaje").textContent = "DELETE: Producto eliminado (simulado).";
}
