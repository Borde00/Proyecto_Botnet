# Proyecto_Botnet

**Autor:** Borde00
**Fecha:** 2025-07-10  

---

## Descripción

Este proyecto implementa una pequeña botnet en Python, dividida en dos componentes:

- **Servidor C2 (`src/Botnet.py`)**  
  Orquesta la red de bots, recibe conexiones de los clientes infectados, envía comandos y recopila resultados.  

- **Cliente infectado (`src/Client.py`)**  
  Se conecta al servidor C2, espera órdenes, ejecuta ataques (hydra, slowloris, hping3, nmap…) y devuelve los resultados.

> ⚠️ **Aviso legal**: Este código es solo para fines educativos y de investigación. Su uso contra sistemas sin autorización es ilegal y puede acarrear responsabilidades.

---

## Estructura del proyecto

```text
Botnet/
├── src/
│   ├── botnet.py       # Código del servidor C2
│   └── client.py       # Código del cliente/bot
├── docs/
│   └── architecture.md # Descripción de la arquitectura C2 ↔ cliente
├── .gitignore          # Ficheros y carpetas a ignorar por Git
├── README.md           
├── LICENSE             # Licencia MIT
└── requirements.txt    # Dependencias Python
