#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar todo el flujo del usuario
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE_URL = f"{BASE_URL}/api"

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(step, message):
    print(f"\n{Colors.BLUE}{Colors.BOLD}[PASO {step}]{Colors.ENDC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.ENDC}")

def print_info(message):
    print(f"   {Colors.BLUE}ℹ️ {message}{Colors.ENDC}")

class FlujoTest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_data = None
        self.productos = []
        self.carrito = []
        self.pedidos = []
        self.favoritos = []
        
    def test_connection(self):
        """Paso 1: Verificar conexión al servidor"""
        print_step(1, "Verificando conexión al servidor...")
        try:
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print_success("Servidor respondiendo correctamente")
                return True
            else:
                print_error(f"Servidor respondió con código {response.status_code}")
                return False
        except Exception as e:
            print_error(f"No se pudo conectar al servidor: {e}")
            return False
    
    def test_login(self):
        """Paso 2: Probar login"""
        print_step(2, "Probando login...")
        try:
            login_data = {
                "username": "cliente1",
                "password": "cliente123"
            }
            
            response = self.session.post(f"{API_BASE_URL}/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_data = data.get("user")
                
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print_success(f"Login exitoso como {self.user_data.get('rol', 'usuario')}")
                print_info(f"Usuario: {self.user_data.get('username', 'N/A')}")
                print_info(f"ID: {self.user_data.get('id', 'N/A')}")
                return True
            else:
                print_error(f"Login falló con código {response.status_code}")
                print_error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error en login: {e}")
            return False
    
    def test_productos(self):
        """Paso 3: Cargar productos"""
        print_step(3, "Cargando productos...")
        try:
            response = self.session.get(f"{API_BASE_URL}/productos/")
            
            if response.status_code == 200:
                self.productos = response.json()
                if not self.productos:
                    print_warning("La API devolvió una lista de productos vacía.")
                    return False
                
                print_success(f"Se cargaron {len(self.productos)} productos")
                
                # Mostrar algunos productos
                for i, producto in enumerate(self.productos[:3]):
                    print_info(f"  {i+1}. {producto.get('nombre', 'N/A')} - ${producto.get('precio_actual', 'N/A')}")
                return True
            else:
                print_error(f"Error al cargar productos: {response.status_code}")
                print_error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error al cargar productos: {e}")
            return False
    
    def test_carrito(self):
        """Paso 4: Probar carrito"""
        print_step(4, "Probando funcionalidad del carrito...")
        
        if not self.productos:
            print_warning("No hay productos para agregar al carrito")
            return False
        
        try:
            # Obtener carrito actual
            response = self.session.get(f"{API_BASE_URL}/carrito/")
            if response.status_code == 200:
                self.carrito = response.json()
                print_info(f"Carrito actual: {len(self.carrito)} items")
            
            # Agregar producto al carrito
            producto_a_agregar = self.productos[0]
            item_data = {
                "producto_id": producto_a_agregar["id"],
                "cantidad": 1
            }
            
            response = self.session.post(f"{API_BASE_URL}/carrito/agregar", json=item_data)
            
            if response.status_code == 200:
                print_success(f"Producto '{producto_a_agregar.get('nombre', 'N/A')}' agregado al carrito")
                
                # Verificar carrito actualizado
                response_get = self.session.get(f"{API_BASE_URL}/carrito/")
                if response_get.status_code == 200:
                    self.carrito = response_get.json()
                    print_info(f"Carrito actualizado: {len(self.carrito)} items")
                    return True
                else:
                    print_error("No se pudo verificar el carrito actualizado.")
                    return False
            else:
                print_error(f"Error al agregar al carrito: {response.status_code}")
                print_error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error en carrito: {e}")
            return False

    def test_favoritos(self):
        """Paso 5: Probar favoritos"""
        print_step(5, "Probando funcionalidad de favoritos...")
        
        if not self.productos:
            print_warning("No hay productos para agregar a favoritos.")
            return False
        
        try:
            # Obtener favoritos actuales
            response_get = self.session.get(f"{API_BASE_URL}/favoritos/")
            if response_get.status_code == 200:
                self.favoritos = response_get.json()
                print_info(f"Favoritos actuales: {len(self.favoritos)} items")
            
            # Agregar producto a favoritos
            producto_a_agregar = self.productos[1] # Usamos el segundo producto
            
            response = self.session.post(f"{API_BASE_URL}/favoritos/toggle/{producto_a_agregar['id']}")
            
            if response.status_code == 200:
                print_success(f"Toggle de favorito para '{producto_a_agregar.get('nombre', 'N/A')}' exitoso.")
                
                # Verificar favoritos actualizados
                response_get_after = self.session.get(f"{API_BASE_URL}/favoritos/")
                if response_get_after.status_code == 200:
                    self.favoritos = response_get_after.json()
                    print_info(f"Favoritos actualizados: {len(self.favoritos)} items")
                    
                    # Verificar si el producto está en la lista de favoritos
                    if any(fav['producto']['id'] == producto_a_agregar['id'] for fav in self.favoritos):
                        print_success("El producto se encuentra en la lista de favoritos.")
                    else:
                        print_warning("El producto fue eliminado de favoritos (ya existía).")
                    return True
                else:
                    print_error("No se pudo verificar la lista de favoritos actualizada.")
                    return False
            else:
                print_error(f"Error al agregar a favoritos: {response.status_code}")
                print_error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error en favoritos: {e}")
            return False

    def test_webpay(self):
        """Paso 6: Probar creación de transacción Webpay"""
        print_step(6, "Probando creación de transacción Webpay...")
        
        if not self.carrito:
            print_warning("El carrito está vacío, no se puede crear transacción.")
            return True # No es un error crítico si el carrito está vacío

        try:
            response = self.session.post(f"{API_BASE_URL}/pagos/crear-transaccion-webpay")
            
            if response.status_code == 200:
                data = response.json()
                print_success("Transacción Webpay creada exitosamente")
                print_info(f"Token: {data.get('token', 'N/A')}")
                print_info(f"Total: ${data.get('total', 'N/A')}")
                print_info(f"URL: {data.get('url', 'N/A')}")
                return True
            else:
                print_error(f"Error al crear transacción Webpay: {response.status_code}")
                print_error(f"Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Error en Webpay: {e}")
            return False
    
    def test_dashboard(self):
        """Paso 7: Probar dashboard del cliente"""
        print_step(7, "Probando dashboard del cliente...")
        
        try:
            endpoints = {
                "perfil": "/usuarios/me",
                "pedidos": "/pedidos/",
            }
            
            all_ok = True
            for name, endpoint in endpoints.items():
                response = self.session.get(f"{API_BASE_URL}{endpoint}")
                if response.status_code == 200:
                    print_success(f"Endpoint '{name}' cargado correctamente.")
                else:
                    print_error(f"Error al cargar endpoint '{name}': {response.status_code} - {response.text}")
                    all_ok = False
            
            return all_ok
                
        except Exception as e:
            print_error(f"Error al probar el dashboard: {e}")
            return False
    
    def run_full_test(self):
        """Ejecutar toda la secuencia de pruebas"""
        print_info("========================================")
        print_info("  INICIANDO PRUEBA DE FLUJO COMPLETO")
        print_info("========================================")
        
        if not self.test_connection():
            print_error("Prueba fallida: No se pudo conectar al servidor.")
            return

        if not self.test_login():
            print_error("Prueba fallida: El login no funcionó.")
            return
            
        if not self.test_productos():
            print_error("Prueba fallida: No se pudieron cargar los productos.")
            return

        if not self.test_carrito():
            print_warning("El paso del carrito falló, continuando con las demás pruebas.")
            
        if not self.test_favoritos():
            print_warning("El paso de favoritos falló, continuando con las demás pruebas.")

        if not self.test_webpay():
            print_warning("El paso de Webpay falló, continuando con las demás pruebas.")

        if not self.test_dashboard():
            print_error("Prueba fallida: El dashboard tiene errores.")

        print_info("\n========================================")
        print_info("     PRUEBA DE FLUJO FINALIZADA")
        print_info("========================================")

def main():
    """Función principal"""
    tester = FlujoTest()
    tester.run_full_test()

if __name__ == "__main__":
    main() 