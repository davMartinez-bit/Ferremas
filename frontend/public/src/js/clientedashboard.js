 const API_BASE_URL = "http://localhost:8000/api";

document.addEventListener("DOMContentLoaded", async () => {
  // Verificar autenticación
  const token = localStorage.getItem("token");
  const rol = localStorage.getItem("rol");
  
  if (!token || rol !== "cliente") {
    alert("Acceso no autorizado. Redirigiendo al login...");
    window.location.href = "login.html";
    return;
  }

  // Mostrar nombre de usuario
  document.getElementById("usernameDisplay").textContent = `Bienvenido, ${localStorage.getItem("username") || 'Cliente'}`;
  
  // Cargar categorías
  await loadCategories();
  
  // Cargar productos destacados por defecto
  await getFeaturedProducts('promociones');
});

async function loadCategories() {
  try {
    const response = await fetch(`${API_BASE_URL}/categorias/`, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });
    
    if (!response.ok) throw new Error("Error al cargar categorías");
    
    const categorias = await response.json();
    const select = document.getElementById("categoryFilter");
    
    categorias.forEach(categoria => {
      const option = document.createElement("option");
      option.value = categoria.nombre;
      option.textContent = categoria.nombre;
      select.appendChild(option);
    });
  } catch (error) {
    console.error("Error:", error);
    alert("Error al cargar categorías");
  }
}

async function searchProducts() {
  const searchTerm = document.getElementById("searchTerm").value.trim();
  const resultado = document.getElementById("resultado");
  
  if (!searchTerm) {
    alert("Por favor ingrese un término de búsqueda");
    return;
  }

  try {
    // Primero intentamos buscar por código exacto
    const response = await fetch(`${API_BASE_URL}/productos/${searchTerm}`, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });

    if (response.ok) {
      const producto = await response.json();
      displayProducts([producto]);
      return;
    }

    // Si no encuentra por código, buscamos por nombre
    const nameResponse = await fetch(`${API_BASE_URL}/productos/?nombre=${searchTerm}`, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });

    if (!nameResponse.ok) throw new Error("Error en la búsqueda");

    const productos = await nameResponse.json();
    displayProducts(productos);

  } catch (error) {
    console.error("Error:", error);
    resultado.innerHTML = `<p class="error">No se encontraron productos</p>`;
  }
}

async function filterByCategory() {
  const category = document.getElementById("categoryFilter").value;
  const resultado = document.getElementById("resultado");
  
  if (!category) {
    alert("Seleccione una categoría");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/productos/?categoria=${category}`, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });

    if (!response.ok) throw new Error("Error al filtrar por categoría");

    const productos = await response.json();
    displayProducts(productos);

  } catch (error) {
    console.error("Error:", error);
    resultado.innerHTML = `<p class="error">Error al cargar productos de la categoría</p>`;
  }
}

async function getFeaturedProducts(type) {
  const resultado = document.getElementById("resultado");
  
  try {
    let endpoint;
    if (type === 'promociones') {
      endpoint = `${API_BASE_URL}/promociones/`;
    } else if (type === 'lanzamientos') {
      endpoint = `${API_BASE_URL}/lanzamientos/`;
    } else {
      endpoint = `${API_BASE_URL}/productos-destacados/`;
    }

    const response = await fetch(endpoint, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });

    if (!response.ok) throw new Error("Error al cargar productos destacados");

    const productos = await response.json();
    displayProducts(type === 'productos-destacados' ? productos : productos);

  } catch (error) {
    console.error("Error:", error);
    resultado.innerHTML = `<p class="error">Error al cargar productos destacados</p>`;
  }
}

function displayProducts(productos) {
  const resultado = document.getElementById("resultado");
  resultado.innerHTML = "";

  if (!productos || productos.length === 0) {
    resultado.innerHTML = `<p>No se encontraron productos</p>`;
    return;
  }

  productos.forEach(prod => {
    const item = document.createElement("div");
    item.className = "producto";
    
    // Formatear precio
    const precio = prod.precio_actual ? 
      new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(prod.precio_actual) : 
      'Precio no disponible';
    
    // Mostrar historial de precios si está disponible
    let historialHTML = '';
    if (prod.historial_precios && prod.historial_precios.length > 0) {
      historialHTML = `<div class="price-history">
        <h4>Historial de precios:</h4>
        <ul>
          ${prod.historial_precios.map(hist => `
            <li>${new Date(hist.fecha).toLocaleDateString()}: ${hist.valor}</li>
          `).join('')}
        </ul>
      </div>`;
    }

    item.innerHTML = `
      <h3>${prod.nombre}</h3>
      <p><strong>Código:</strong> ${prod.codigo}</p>
      <p>${prod.descripcion || 'Sin descripción'}</p>
      <p><strong>Marca:</strong> ${prod.marca || 'No especificada'}</p>
      <p><strong>Precio:</strong> ${precio}</p>
      <p><strong>Stock:</strong> ${prod.stock || 0} unidades</p>
      ${historialHTML}
      <button onclick="initPayment('${prod.codigo}', ${prod.precio_actual || 0})">Comprar</button>
    `;
    resultado.appendChild(item);
  });
}

async function convertCurrency() {
  const amount = parseFloat(document.getElementById("amount").value);
  const fromCurrency = document.getElementById("fromCurrency").value;
  const toCurrency = document.getElementById("toCurrency").value;
  const resultDiv = document.getElementById("conversionResult");

  

  // Si es la misma moneda, no hacemos conversión
  if (fromCurrency === toCurrency) {
    resultDiv.innerHTML = `<p>El monto es el mismo: ${amount} ${fromCurrency}</p>`;
    return;
  }

  try {
    // Para CLP, usamos la API del Banco Central
    if (fromCurrency === 'CLP' || toCurrency === 'CLP') {
      const moneda = fromCurrency === 'CLP' ? toCurrency : fromCurrency;
      const response = await fetch(`${API_BASE_URL}/divisas/${moneda}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      });

      if (!response.ok) throw new Error("Error al obtener tasa de cambio");

      const data = await response.json();
      let convertedAmount;

      if (fromCurrency === 'CLP') {
        // Convertir de CLP a otra moneda
        convertedAmount = amount / data.valor;
        resultDiv.innerHTML = `
          <p>${amount.toFixed(2)} CLP = ${convertedAmount.toFixed(2)} ${toCurrency}</p>
          <p>Tasa: 1 ${toCurrency} = ${data.valor} CLP</p>
        `;
      } else {
        // Convertir de otra moneda a CLP
        convertedAmount = amount * data.valor;
        resultDiv.innerHTML = `
          <p>${amount.toFixed(2)} ${fromCurrency} = ${convertedAmount.toFixed(2)} CLP</p>
          <p>Tasa: 1 ${fromCurrency} = ${data.valor} CLP</p>
        `;
      }
    } else {
      // Conversión entre monedas extranjeras (USD-EUR, etc.)
      // Primero convertimos a CLP y luego a la moneda destino
      const responseFrom = await fetch(`${API_BASE_URL}/divisas/${fromCurrency}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      });

      const responseTo = await fetch(`${API_BASE_URL}/divisas/${toCurrency}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      });

      if (!responseFrom.ok || !responseTo.ok) throw new Error("Error al obtener tasas de cambio");

      const dataFrom = await responseFrom.json();
      const dataTo = await responseTo.json();

      // Convertir a CLP primero
      const amountInCLP = amount * dataFrom.valor;
      // Luego convertir a moneda destino
      const convertedAmount = amountInCLP / dataTo.valor;

      resultDiv.innerHTML = `
        <p>${amount.toFixed(2)} ${fromCurrency} = ${convertedAmount.toFixed(2)} ${toCurrency}</p>
        <p>Tasas:</p>
        <ul>
          <li>1 ${fromCurrency} = ${dataFrom.valor} CLP</li>
          <li>1 ${toCurrency} = ${dataTo.valor} CLP</li>
        </ul>
      `;
    }
  } catch (error) {
    console.error("Error:", error);
    resultDiv.innerHTML = `<p class="error">Error al convertir divisas</p>`;
  }
}

async function sendMessage() {
  const messageContent = document.getElementById("messageContent").value.trim();
  
  if (!messageContent) {
    alert("Por favor escriba un mensaje");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/contacto/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({
        mensaje: messageContent,
        usuario: localStorage.getItem("username") || 'Cliente'
      })
    });

    if (!response.ok) throw new Error("Error al enviar mensaje");

    alert("Mensaje enviado con éxito");
    document.getElementById("messageContent").value = "";
  } catch (error) {
    console.error("Error:", error);
    alert("Error al enviar mensaje");
  }
}

async function initPayment(productCode, amount) {
  try {
    // Primero creamos la transacción en WebPay
    const response = await fetch(`${API_BASE_URL}/webpay/iniciar`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({
        buy_order: `ORD-${Date.now()}`,
        session_id: localStorage.getItem("username") || 'guest',
        amount: amount,
        return_url: `${window.location.origin}/pago-exitoso.html`
      })
    });

    if (!response.ok) throw new Error("Error al iniciar pago");

    const data = await response.json();
    
    // Redirigimos al usuario a WebPay para completar el pago
    window.location.href = data.url;
    
  } catch (error) {
    console.error("Error:", error);
    alert("Error al iniciar el proceso de pago");
  }
}

function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}   