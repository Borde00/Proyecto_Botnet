# Proyecto_Botnet

Proyecto académico y de laboratorio orientado al estudio de arquitecturas C2, automatización de clientes remotos y análisis de ejecución distribuida en entornos controlados.

> [!WARNING]
> **Este proyecto ha sido desarrollado exclusivamente con fines educativos, formativos y de investigación en ciberseguridad.**
>  
> Su uso debe limitarse a laboratorios aislados, máquinas virtuales propias o entornos donde exista autorización expresa.  
> No debe utilizarse contra sistemas, redes o servicios de terceros sin permiso.

---

## Descripción

Este proyecto implementa una arquitectura cliente-servidor en Python inspirada en un modelo C2 (Command and Control) para prácticas de laboratorio, pruebas controladas y análisis de comunicación remota entre nodos.

El sistema se compone de:

- Un **servidor C2** que recibe conexiones, mantiene una lista de clientes activos y centraliza el envío de órdenes.
- Un **cliente** que se conecta al servidor, recibe instrucciones y devuelve resultados.
- Un documento de **arquitectura** que explica el flujo de comunicación entre ambos componentes.

El objetivo principal del proyecto es **aprender**, **experimentar** y **documentar** conceptos relacionados con:
- Comunicación socket TCP.
- Coordinación de clientes remotos.
- Automatización de tareas desde un nodo central.
- Gestión de resultados y ejecución distribuida.
- Diseño de laboratorios defensivos y de investigación.

---

## Objetivos del proyecto

- Comprender cómo funciona una arquitectura C2 a nivel técnico.
- Practicar programación en Python orientada a redes y automatización.
- Simular escenarios de laboratorio para formación en ciberseguridad.
- Documentar el flujo entre servidor y clientes de forma clara.
- Servir como base para futuras mejoras, refactorización y hardening del código.

---

## Arquitectura

A alto nivel, el flujo es el siguiente:

1. El servidor C2 queda a la escucha en una IP y un puerto definidos.
2. Los clientes se conectan al servidor de forma remota.
3. El operador central gestiona los clientes conectados desde un menú.
4. El servidor envía órdenes a los clientes.
5. Los clientes ejecutan la lógica correspondiente y devuelven los resultados.
6. El servidor recibe, agrupa y muestra la salida al operador.

Para una explicación más detallada del diseño, consulta el archivo:

- `architecture.md`

---

## Tecnologías utilizadas

- **Python 3**
- **Sockets TCP**
- **Threading**
- **Colorama**
- Integración experimental con herramientas externas del sistema para laboratorio y análisis técnico

---

## Estructura del proyecto

```text
Proyecto_Botnet/
├── Botnet.py          # Servidor C2
├── Cliente.py         # Cliente remoto
├── architecture.md    # Documento de arquitectura
├── README.md
├── LICENSE
├── requirements.txt
└── Installing         # Notas de instalación
```

---

## Entorno recomendado

Para utilizar este proyecto de forma responsable, se recomienda:

- Un laboratorio aislado.
- Máquinas virtuales o equipos de pruebas.
- Red privada o NAT de laboratorio.
- Sistemas bajo tu control o con autorización.
- Entorno de análisis sin exposición pública.

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Proyecto_Botnet
```

### 2. Crear un entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows:

```powershell
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Revisar configuración

Antes de ejecutar cualquier prueba, revisa y adapta:
- La IP del servidor.
- El puerto de escucha.
- Los nombres y rutas de los archivos auxiliares.
- Las dependencias externas necesarias para el entorno de laboratorio.

---

## Funcionamiento general

El proyecto sigue una lógica simple:

- El **servidor** recibe conexiones entrantes y administra clientes activos.
- El **cliente** establece conexión con el servidor y espera instrucciones.
- Los resultados se devuelven al servidor y se presentan desde consola.

Este repositorio debe entenderse como una **base educativa** para estudiar:
- Diseño de herramientas distribuidas.
- Comunicación cliente-servidor.
- Automatización y orquestación.
- Refactorización y mejora segura de código.

---

## Vídeo de demostración

Puedes añadir aquí un vídeo mostrando el funcionamiento del proyecto en un **entorno de laboratorio controlado**.

### Opción 1: enlace directo

```md
## Vídeo de demostración

[Ver vídeo de funcionamiento](https://www.youtube.com/watch?v=TU_VIDEO_ID)
```

### Opción 2: miniatura clicable de YouTube

```md
## Vídeo de demostración

[
```

### Qué enseñar en el vídeo

Te recomiendo que el vídeo muestre:

- Presentación breve del objetivo del proyecto.
- Explicación de la arquitectura C2 ↔ cliente.
- Configuración del entorno de laboratorio.
- Ejecución controlada del servidor y del cliente.
- Visualización de la recepción de resultados.
- Cierre con advertencia ética y legal.

---

## Posibles mejoras

- Refactorizar la estructura del proyecto en carpetas `src/` y `docs/`.
- Mejorar validaciones y manejo de errores.
- Añadir registro de eventos (`logging`).
- Separar configuración en un archivo `.env` o `config.py`.
- Incluir pruebas unitarias.
- Documentar mejor los módulos.
- Añadir hardening del canal de comunicación.
- Mejorar la trazabilidad de resultados.

---

## Aviso ético y legal

Este repositorio se comparte únicamente con fines educativos y de investigación.

El autor no promueve el uso indebido del software ni su despliegue fuera de entornos controlados.  
Cualquier uso no autorizado contra infraestructuras ajenas puede ser ilegal y es responsabilidad exclusiva de quien lo ejecute.

---

## Licencia

Este proyecto se distribuye bajo licencia MIT.  
Consulta el archivo `LICENSE` para más información.

---

## Autor

**Borde00**

Proyecto en evolución, creado como práctica de aprendizaje, documentación técnica y experimentación en laboratorio.
