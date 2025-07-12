# Arquitectura de Proyecto_Botnet

Este documento describe la estructura y el flujo de comunicación entre el **Servidor C2** y los **Clientes/Bots**.

---

## 1. Componentes principales

1. **Servidor C2 (`src/Botnet.py`)**  
   - Escucha conexiones entrantes de bots en un puerto TCP (por defecto `8888`).  
   - Mantiene una lista de sockets de bots activos (`bots[]`).  
   - Ofrece un menú interactivo para enviar comandos de ataque y visualizar resultados.  
   - Agrupa y enseña los resultados recibidos según el tipo de ataque.

2. **Cliente/Bot (`src/Cliente.py`)**  
   - Se conecta en bucle al servidor C2 (`HOST:PORT`).  
   - Recibe comandos y, según la palabra clave, ejecuta uno de los módulos de ataque:  
     - **HYDRA**: fuerza bruta SSH (usa ficheros de usuarios/contraseñas enviados codificados en Base64).  
     - **SLOWLORIS**: ataque HTTP lento (lanza `slowhttptest` y luego verifica con `requests`).  
     - **HPING3**: flood de paquetes SYN con `hping3`.  
     - **NMAP**: escaneo de puertos con `nmap`.  
   - Devuelve los resultados como cadenas de texto al servidor.

---

## 2. Flujo de comunicación

```text
+-----------+                                +-----------+
|  C2 Server|                                |   Cliente |   
+-----------+                                +-----------+
      │                                           │
      │ 1. START → bind en HOST:PORT              │
      │──────────────────────────────────────────►│
      │                                           │
      │ 2. ACCEPT conexión de bot                 │
      │◄──────────────────────────────────────────│
      │ socket_bot ∈ bots[]                       │
      │                                           │
      │ 3. Enviar comando de ataque               │
      │   e.g. “HYDRA user@host”                  │
      │──────────────────────────────────────────►│
      │                                           │
      │                4. Ejecutar módulo         │
      │                (p.ej. hydra…)             │
      │                                           │
      │                5. Recoger salida          │
      │                y formatear                 │
      │                                           │
      │◄──────────────────────────────────────────│
      │   6. Almacenar resultado en `results[]`    │
      │                                           │
      │ 7. Mostrar resultados al operador         │
      │                                           │
