# Proyecto_Botnet

Proyecto académico de laboratorio orientado al estudio práctico de arquitecturas C2 (Command & Control), comunicación distribuida cliente-servidor y análisis de técnicas de ataque en entornos controlados.

> [!WARNING]
> **Este proyecto ha sido desarrollado exclusivamente con fines educativos, formativos y de investigación en ciberseguridad.**
>
> Su uso debe limitarse estrictamente a laboratorios aislados, máquinas virtuales propias o entornos con autorización expresa.
> Queda prohibido su uso contra sistemas, redes o servicios de terceros sin permiso explícito.
> Cualquier uso ilícito es responsabilidad exclusiva de quien lo ejecute.

---

## Descripción

Este proyecto implementa en Python una arquitectura C2 funcional compuesta por un **servidor centralizado** (`Botnet.py`) y un **cliente/bot** (`Cliente.py`) que se conecta a él de forma persistente. El operador gestiona los bots desde un menú interactivo en consola, enviando comandos de ataque y recibiendo los resultados en tiempo real.

El objetivo principal es **aprender, experimentar y documentar** conceptos clave de:

- Comunicación TCP mediante sockets.
- Coordinación y gestión de clientes remotos.
- Transferencia de ficheros codificados en Base64.
- Ejecución distribuida de módulos de ataque.
- Diseño de laboratorios de ciberseguridad defensiva.

---

## Módulos de ataque implementados

| Módulo | Comando C2 | Herramienta | Descripción |
|---|---|---|---|
| SSH Brute Force | `HYDRA ssh ssh://HOST:PORT users.txt pass.txt` | `hydra` | Fuerza bruta SSH con listas de credenciales enviadas en Base64 |
| HTTP Flood | `SLOWLORIS HOST PORT DURATION` | `slowhttptest` | Ataque Slowloris con verificación de disponibilidad HTTP |
| SYN Flood | `HPING3_SYN HOST PORT DURATION` | `hping3` | Flood de paquetes SYN con IP spoofing aleatorio |
| Port Scan | `NMAP_SCAN HOST` | `nmap` | Escaneo de servicios en rango de puertos 64000–64300 |

---

## Arquitectura

El flujo de comunicación sigue el siguiente esquema:

```text
+-----------+                                +-----------+
|  C2 Server|                                |  Cliente  |
+-----------+                                +-----------+
      │                                           │
      │  1. bind en HOST:PORT (8888)              │
      │──────────────────────────────────────────►│
      │                                           │
      │  2. ACCEPT conexión del bot               │
      │◄──────────────────────────────────────────│
      │  socket_bot ∈ bots[]                      │
      │                                           │
      │  3. [HYDRA] SEND_FILE users.txt <b64>     │
      │──────────────────────────────────────────►│
      │  3. [HYDRA] SEND_FILE password.txt <b64>  │
      │──────────────────────────────────────────►│
      │                                           │
      │  4. Enviar comando de ataque              │
      │     e.g. "HYDRA ssh ssh://HOST:22 ..."    │
      │──────────────────────────────────────────►│
      │                                           │
      │               5. Ejecutar módulo          │
      │               (hydra / hping3 / nmap…)    │
      │                                           │
      │◄──────────────────────────────────────────│
      │  6. RESULT → results[]                    │
      │                                           │
      │  7. Mostrar resultados al operador        │
```

Para el detalle completo del diseño, consulta [`architecture.md`](architecture.md).

---

## Tecnologías y dependencias

### Python (pip)

```bash
pip install -r requirements.txt
```

| Paquete | Uso |
|---|---|
| `colorama` | Colores en consola (banner, menú, resultados) |
| `requests` | Verificación de disponibilidad HTTP tras Slowloris |

### Herramientas externas del sistema

| Herramienta | Módulo que la usa | Instalación (Debian/Ubuntu) |
|---|---|---|
| `hydra` | SSH Brute Force | `sudo apt install hydra` |
| `slowhttptest` | HTTP Flood | `sudo apt install slowhttptest` |
| `hping3` | SYN Flood | `sudo apt install hping3` |
| `nmap` | Port Scan | `sudo apt install nmap` |

---

## Estructura del proyecto

```text
Proyecto_Botnet/
├── Botnet.py          # Servidor C2 — menú interactivo y gestión de bots
├── Cliente.py         # Cliente/Bot — ejecuta módulos de ataque
├── architecture.md    # Diagrama y flujo de comunicación
├── README.md
├── LICENSE
├── requirements.txt   # Dependencias Python
└── Installing         # Notas de instalación adicionales
```

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto_Botnet
```

### 2. Crear entorno virtual e instalar dependencias Python

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 3. Instalar dependencias del sistema

```bash
sudo apt update
sudo apt install hydra slowhttptest hping3 nmap -y
```

### 4. Ajustar la configuración

Antes de ejecutar, edita las siguientes variables en cada script:

**`Botnet.py`** — IP y puerto de escucha del servidor C2:
```python
server.bind(('192.168.10.16', 8888))   # ← cambia por tu IP de laboratorio
```

**`Cliente.py`** — IP y puerto del servidor C2 al que conectar:
```python
C2_SERVER = '192.168.56.11'            # ← IP del servidor C2
C2_PORT   = 8888
```

---

## Uso

### Iniciar el servidor C2

```bash
python3 Botnet.py
```

El servidor quedará a la escucha en el puerto `8888` mostrando el menú interactivo:

```
Menu Principal
1. Listar bots conectados
2. Iniciar ataque
3. Salir
```

### Conectar un cliente/bot

En cada máquina bot (o VM de laboratorio), ejecuta:

```bash
python3 Cliente.py
```

El cliente se conecta automáticamente al C2 y se reconecta cada 5 segundos si pierde la conexión.

### Flujo de ataque

1. Selecciona **opción 2** en el menú del servidor.
2. Elige el tipo de ataque (1–4).
3. Introduce los parámetros solicitados (IP objetivo, puerto, duración, etc.).
4. El servidor envía el comando a todos los bots activos.
5. Los resultados se muestran automáticamente en consola una vez finalizado el ataque.

---

## Entorno recomendado

Para un uso responsable y seguro, se recomienda ejecutar este proyecto en:

- Red privada o NAT de laboratorio aislada de Internet.
- Máquinas virtuales (VirtualBox, VMware, Proxmox) o contenedores Docker.
- Sistemas operativos de pruebas bajo tu propio control.
- Kali Linux como SO base para disponer de las herramientas externas preinstaladas.

---

## Posibles mejoras

- [ ] Refactorizar en estructura `src/` y `docs/`.
- [ ] Separar configuración en `.env` o `config.py`.
- [ ] Añadir cifrado del canal de comunicación (TLS/SSL).
- [ ] Implementar autenticación entre servidor y clientes.
- [ ] Registrar eventos con el módulo `logging`.
- [ ] Añadir pruebas unitarias por módulo de ataque.
- [ ] Soporte para comandos en paralelo a múltiples bots simultáneamente.
- [ ] Dashboard web de gestión de bots.

---

## Aviso ético y legal

Este repositorio se comparte únicamente con fines educativos y de investigación en ciberseguridad.

El autor no promueve el uso indebido de este software ni su despliegue fuera de entornos controlados y autorizados. El uso no autorizado contra infraestructuras ajenas puede constituir un delito tipificado en el artículo 197 bis y siguientes del Código Penal español, así como en legislaciones equivalentes de otros países.

---

## Licencia

Distribuido bajo licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE) para más información.

---

## Autor

**Borde00**

Proyecto en evolución, creado como práctica de aprendizaje, documentación técnica y experimentación en entornos de laboratorio de ciberseguridad.
