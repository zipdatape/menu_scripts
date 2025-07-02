#!/usr/bin/env python3
import os
import getpass
import subprocess
import shutil
import itertools
import time
import threading
import yaml
import json
import requests
import re
from datetime import datetime

def print_status(message, status, index=None, total=None):
    checkmark = '\u2714'
    crossmark = '\u274C'
    green = '\033[92m'
    red = '\033[91m'
    reset = '\033[0m'
    if index is not None and total is not None:
        progress = f"[{index}/{total}]"
    else:
        progress = ""
    
    if status == 0:
        print(f"{progress} {message} [{green}{checkmark}{reset}]")
    else:
        print(f"{progress} {message} [{red}{crossmark}{reset}]")

def is_root():
    return os.geteuid() == 0

def get_all_users():
    users = []
    with open('/etc/passwd', 'r') as f:
        for line in f:
            if '/home' in line:
                users.append(line.split(':')[0])
    return users

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def get_latest_docker_version():
    """Obtiene la versión más reciente de Docker desde GitHub"""
    try:
        response = requests.get('https://api.github.com/repos/docker/docker-ce/releases/latest')
        if response.status_code == 200:
            data = response.json()
            return data['tag_name'].replace('v', '')
    except:
        pass
    return "24.0.7"  # Versión por defecto

def get_latest_docker_compose_version():
    """Obtiene la versión más reciente de Docker Compose desde GitHub"""
    try:
        response = requests.get('https://api.github.com/repos/docker/compose/releases/latest')
        if response.status_code == 200:
            data = response.json()
            return data['tag_name']
    except:
        pass
    return "v2.23.3"  # Versión por defecto

def install_docker_improved():
    """Instala Docker con la versión más reciente"""
    print("Obteniendo la versión más reciente de Docker...")
    docker_version = get_latest_docker_version()
    compose_version = get_latest_docker_compose_version()
    
    print(f"Instalando Docker {docker_version} y Docker Compose {compose_version}...")
    
    # Verificar si Docker ya está instalado
    if subprocess.call(["which", "docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        print("Docker ya está instalado. Verificando versión...")
        current_version = subprocess.getoutput("docker --version")
        print(f"Versión actual: {current_version}")
        choice = input("¿Deseas reinstalar Docker? (si/no): ").strip().lower()
        if choice not in ['si', 's']:
            print("Instalación cancelada.")
            return
    
    # Método 1: Instalación desde repositorio oficial (recomendado)
    print("Método 1: Instalación desde repositorio oficial...")
    if install_docker_from_repo():
        return
    
    # Método 2: Instalación usando script oficial (fallback)
    print("Método 2: Instalación usando script oficial...")
    if install_docker_from_script():
        return
    
    # Método 3: Instalación usando apt (último recurso)
    print("Método 3: Instalación usando apt...")
    if install_docker_from_apt():
        return
    
    print_status("Error: No se pudo instalar Docker con ningún método", 1)

def install_docker_from_repo():
    """Instala Docker desde el repositorio oficial"""
    try:
        # Instalar dependencias
        print("Instalando dependencias...")
        deps_commands = [
            'sudo apt-get update',
            'sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release'
        ]
        
        for command in deps_commands:
            if not run_command(command):
                return False
        
        # Configurar repositorio Docker
        print("Configurando repositorio Docker...")
        
        # Eliminar archivo de clave existente si existe
        if os.path.exists('/usr/share/keyrings/docker-archive-keyring.gpg'):
            run_command('sudo rm -f /usr/share/keyrings/docker-archive-keyring.gpg')
        
        # Agregar clave GPG
        gpg_commands = [
            'curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg',
            'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null'
        ]
        
        for command in gpg_commands:
            if not run_command(command):
                return False
        
        # Actualizar repositorios
        if not run_command('sudo apt-get update'):
            return False
        
        # Instalar Docker (sin versión específica para mayor compatibilidad)
        print("Instalando Docker...")
        docker_install_commands = [
            'sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin'
        ]
        
        for command in docker_install_commands:
            if not run_command(command):
                return False
        
        # Configurar Docker
        print("Configurando Docker...")
        docker_config_commands = [
            'sudo systemctl start docker',
            'sudo systemctl enable docker'
        ]
        
        for command in docker_config_commands:
            if not run_command(command):
                return False
        
        # Agregar usuario al grupo docker
        current_user = os.getenv('USER') or os.getenv('SUDO_USER') or 'root'
        if current_user != 'root':
            run_command(f'sudo usermod -aG docker {current_user}')
        
        # Instalar Docker Compose standalone
        print("Instalando Docker Compose...")
        compose_version = get_latest_docker_compose_version()
        compose_commands = [
            f'sudo curl -L "https://github.com/docker/compose/releases/download/{compose_version}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose',
            'sudo chmod +x /usr/local/bin/docker-compose'
        ]
        
        for command in compose_commands:
            if not run_command(command):
                return False
        
        # Verificar instalación
        print("Verificando instalación...")
        if verify_docker_installation():
            print_status("Docker y Docker Compose instalados correctamente desde repositorio oficial", 0)
            print("IMPORTANTE: Debes cerrar sesión y volver a iniciar para que los cambios de grupo surtan efecto.")
            print("Para verificar la instalación, ejecuta: docker --version && docker-compose --version")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error en instalación desde repositorio: {e}")
        return False

def install_docker_from_script():
    """Instala Docker usando el script oficial"""
    try:
        print("Descargando script de instalación oficial...")
        
        # Descargar script oficial
        if not run_command('curl -fsSL https://get.docker.com -o get-docker.sh'):
            return False
        
        # Hacer ejecutable y ejecutar
        if not run_command('sudo sh get-docker.sh'):
            return False
        
        # Limpiar script
        run_command('rm -f get-docker.sh')
        
        # Agregar usuario al grupo docker
        current_user = os.getenv('USER') or os.getenv('SUDO_USER') or 'root'
        if current_user != 'root':
            run_command(f'sudo usermod -aG docker {current_user}')
        
        # Instalar Docker Compose
        print("Instalando Docker Compose...")
        compose_version = get_latest_docker_compose_version()
        compose_commands = [
            f'sudo curl -L "https://github.com/docker/compose/releases/download/{compose_version}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose',
            'sudo chmod +x /usr/local/bin/docker-compose'
        ]
        
        for command in compose_commands:
            if not run_command(command):
                return False
        
        # Verificar instalación
        if verify_docker_installation():
            print_status("Docker y Docker Compose instalados correctamente usando script oficial", 0)
            print("IMPORTANTE: Debes cerrar sesión y volver a iniciar para que los cambios de grupo surtan efecto.")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error en instalación desde script: {e}")
        return False

def install_docker_from_apt():
    """Instala Docker usando apt (último recurso)"""
    try:
        print("Instalando Docker desde repositorios del sistema...")
        
        # Actualizar repositorios
        if not run_command('sudo apt-get update'):
            return False
        
        # Instalar Docker
        if not run_command('sudo apt-get install -y docker.io docker-compose'):
            return False
        
        # Configurar Docker
        docker_config_commands = [
            'sudo systemctl start docker',
            'sudo systemctl enable docker'
        ]
        
        for command in docker_config_commands:
            if not run_command(command):
                return False
        
        # Agregar usuario al grupo docker
        current_user = os.getenv('USER') or os.getenv('SUDO_USER') or 'root'
        if current_user != 'root':
            run_command(f'sudo usermod -aG docker {current_user}')
        
        # Verificar instalación
        if verify_docker_installation():
            print_status("Docker instalado correctamente desde repositorios del sistema", 0)
            print("IMPORTANTE: Debes cerrar sesión y volver a iniciar para que los cambios de grupo surtan efecto.")
            return True
        
        return False
        
    except Exception as e:
        print(f"Error en instalación desde apt: {e}")
        return False

def verify_docker_installation():
    """Verifica que Docker y Docker Compose estén instalados correctamente"""
    try:
        # Verificar Docker
        if subprocess.call(["which", "docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            docker_version_output = subprocess.getoutput("docker --version")
            print_status(f"Docker instalado: {docker_version_output}", 0)
        else:
            print_status("Error: Docker no se instaló correctamente", 1)
            return False
        
        # Verificar Docker Compose
        if subprocess.call(["which", "docker-compose"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            compose_version_output = subprocess.getoutput("docker-compose --version")
            print_status(f"Docker Compose instalado: {compose_version_output}", 0)
        else:
            print_status("Error: Docker Compose no se instaló correctamente", 1)
            return False
        
        # Probar Docker
        if subprocess.call(["sudo", "docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            print_status("Docker funcionando correctamente", 0)
        else:
            print_status("Error: Docker no está funcionando correctamente", 1)
            return False
        
        return True
        
    except Exception as e:
        print(f"Error en verificación: {e}")
        return False

def get_latest_nodejs_version():
    """Obtiene la versión más reciente de Node.js"""
    try:
        response = requests.get("https://api.github.com/repos/nodejs/node/releases/latest")
        if response.status_code == 200:
            data = response.json()
            version = data['tag_name']
            return version
        else:
            print_status("Error al obtener versión de Node.js, usando versión por defecto", 1)
            return "v20.10.0"
    except Exception as e:
        print(f"Error al obtener versión de Node.js: {e}")
        return "v20.10.0"

def install_nvm():
    """Instala NVM (Node Version Manager)"""
    print("Instalando NVM (Node Version Manager)...")
    
    # Obtener la versión más reciente de NVM
    try:
        response = requests.get("https://api.github.com/repos/nvm-sh/nvm/releases/latest")
        if response.status_code == 200:
            data = response.json()
            nvm_version = data['tag_name']
        else:
            nvm_version = "v0.39.0"  # Versión por defecto
    except:
        nvm_version = "v0.39.0"
    
    print(f"Instalando NVM {nvm_version}...")
    
    # Instalar NVM
    install_command = f'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/{nvm_version}/install.sh | bash'
    
    if run_command(install_command):
        print_status("NVM instalado correctamente", 0)
        
        # Configurar variables de entorno
        nvm_config = '''
# NVM Configuration
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \\. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
'''
        
        # Agregar configuración a .bashrc si no existe
        bashrc_path = os.path.expanduser("~/.bashrc")
        if os.path.exists(bashrc_path):
            with open(bashrc_path, 'r') as f:
                content = f.read()
            
            if 'NVM_DIR' not in content:
                with open(bashrc_path, 'a') as f:
                    f.write(nvm_config)
                print_status("Configuración de NVM agregada a .bashrc", 0)
        
        print("Para usar NVM, ejecuta: source ~/.bashrc")
        print("Luego puedes usar comandos como:")
        print("  nvm install node      # Instalar última versión de Node.js")
        print("  nvm install 18.17.0   # Instalar versión específica")
        print("  nvm use 18.17.0       # Cambiar a versión específica")
        print("  nvm list              # Listar versiones instaladas")
        
        return True
    else:
        print_status("Error al instalar NVM", 1)
        return False

def install_nodejs_latest():
    """Instala la versión más reciente de Node.js"""
    print("Instalando Node.js (versión más reciente)...")
    
    # Método 1: Usar NodeSource repository (recomendado)
    commands = [
        'curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -',
        'sudo apt-get install -y nodejs'
    ]
    
    for command in commands:
        if not run_command(command):
            print_status("Error en instalación desde NodeSource", 1)
            break
    else:
        # Verificar instalación
        if subprocess.call(["which", "node"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            node_version = subprocess.getoutput("node --version")
            npm_version = subprocess.getoutput("npm --version")
            print_status(f"Node.js instalado: {node_version}", 0)
            print_status(f"npm instalado: {npm_version}", 0)
            return True
    
    # Método 2: Usar snap como fallback
    print("Intentando instalación con snap...")
    if run_command('sudo snap install node --classic'):
        print_status("Node.js instalado con snap", 0)
        return True
    
    # Método 3: Usar repositorio de Ubuntu como último recurso
    print("Intentando instalación desde repositorio de Ubuntu...")
    if run_command('sudo apt-get update') and run_command('sudo apt-get install -y nodejs npm'):
        print_status("Node.js instalado desde repositorio de Ubuntu", 0)
        return True
    
    print_status("Error: No se pudo instalar Node.js con ningún método", 1)
    return False

def install_nodejs_specific_version():
    """Instala una versión específica de Node.js usando NVM"""
    print("Instalación de versión específica de Node.js")
    print("Nota: Esto requiere NVM (Node Version Manager)")
    
    # Verificar si NVM está instalado
    nvm_check = subprocess.getoutput("command -v nvm")
    if not nvm_check:
        print("NVM no está instalado. ¿Deseas instalarlo primero?")
        choice = input("(si/no): ").strip().lower()
        if choice in ['si', 's']:
            if install_nvm():
                print("NVM instalado. Reinicia tu terminal y ejecuta este comando nuevamente.")
                return
        else:
            print("Instalación cancelada.")
            return
    
    # Mostrar versiones populares
    print("\nVersiones populares de Node.js:")
    print("1. 20.x.x (LTS - Recomendada)")
    print("2. 18.x.x (LTS)")
    print("3. 16.x.x (LTS)")
    print("4. Especificar versión manualmente")
    print("5. Cancelar")
    
    choice = input("Seleccione una opción [1-5]: ").strip()
    
    version_map = {
        '1': '20',
        '2': '18',
        '3': '16'
    }
    
    if choice in version_map:
        version = version_map[choice]
    elif choice == '4':
        version = input("Ingrese la versión (ej: 18.17.0, 20.10.0): ").strip()
    elif choice == '5':
        print("Instalación cancelada.")
        return
    else:
        print("Opción inválida.")
        return
    
    # Comandos para instalar con NVM
    nvm_commands = [
        f'source ~/.bashrc && nvm install {version}',
        f'source ~/.bashrc && nvm use {version}',
        f'source ~/.bashrc && nvm alias default {version}'
    ]
    
    print(f"Instalando Node.js versión {version}...")
    
    for command in nvm_commands:
        if run_command(command):
            print_status(f"Comando ejecutado: {command}", 0)
        else:
            print_status(f"Error en comando: {command}", 1)
    
    print("Instalación completada.")
    print("Para verificar: node --version && npm --version")

def install_pm2():
    """Instala PM2 (Process Manager 2)"""
    print("Instalando PM2 (Process Manager 2)...")
    
    # Verificar si npm está disponible
    if subprocess.call(["which", "npm"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print_status("npm no está instalado. Instalando Node.js primero...", 1)
        if not install_nodejs_latest():
            print_status("Error: No se pudo instalar npm", 1)
            return False
    
    # Instalar PM2 globalmente
    if run_command('sudo npm install -g pm2'):
        print_status("PM2 instalado correctamente", 0)
        
        # Verificar instalación
        if subprocess.call(["which", "pm2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            pm2_version = subprocess.getoutput("pm2 --version")
            print_status(f"PM2 versión: {pm2_version}", 0)
            
            # Configurar PM2 para inicio automático
            print("Configurando PM2 para inicio automático del sistema...")
            startup_command = subprocess.getoutput("pm2 startup")
            print(f"Ejecuta el siguiente comando para completar la configuración:\n{startup_command}")
            
            print("\nComandos útiles de PM2:")
            print("  pm2 start app.js          # Iniciar aplicación")
            print("  pm2 list                  # Listar aplicaciones")
            print("  pm2 stop app_name         # Detener aplicación")
            print("  pm2 restart app_name      # Reiniciar aplicación")
            print("  pm2 delete app_name       # Eliminar aplicación")
            print("  pm2 logs                  # Ver logs")
            print("  pm2 monitor               # Monitor en tiempo real")
            print("  pm2 save                  # Guardar configuración actual")
            
            return True
        else:
            print_status("Error: PM2 no se instaló correctamente", 1)
            return False
    else:
        print_status("Error al instalar PM2", 1)
        return False

def nodejs_submenu():
    """Submenú para Node.js, npm, PM2 y NVM"""
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Node.js y Herramientas")
        print("--------------------------------------------------")
        print("1. Instalar Node.js y npm (versión más reciente)")
        print("2. Instalar NVM (Node Version Manager)")
        print("3. Instalar versión específica de Node.js (requiere NVM)")
        print("4. Instalar PM2 (Process Manager)")
        print("5. Verificar instalaciones")
        print("6. Volver al menú principal")
        print("--------------------------------------------------")
        
        choice = input("Seleccione una opción [1-6]: ").strip()
        
        if choice == '1':
            install_nodejs_latest()
        elif choice == '2':
            install_nvm()
        elif choice == '3':
            install_nodejs_specific_version()
        elif choice == '4':
            install_pm2()
        elif choice == '5':
            verify_nodejs_installations()
        elif choice == '6':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        
        input("Presione [Enter] para continuar...")

def verify_nodejs_installations():
    """Verifica las instalaciones de Node.js, npm, PM2 y NVM"""
    print("Verificando instalaciones de Node.js y herramientas...")
    print("=" * 50)
    
    # Verificar Node.js
    if subprocess.call(["which", "node"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        node_version = subprocess.getoutput("node --version")
        print_status(f"Node.js instalado: {node_version}", 0)
    else:
        print_status("Node.js: No instalado", 1)
    
    # Verificar npm
    if subprocess.call(["which", "npm"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        npm_version = subprocess.getoutput("npm --version")
        print_status(f"npm instalado: {npm_version}", 0)
    else:
        print_status("npm: No instalado", 1)
    
    # Verificar PM2
    if subprocess.call(["which", "pm2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        pm2_version = subprocess.getoutput("pm2 --version")
        print_status(f"PM2 instalado: {pm2_version}", 0)
        
        # Mostrar aplicaciones PM2
        pm2_list = subprocess.getoutput("pm2 list")
        if pm2_list:
            print("Aplicaciones PM2:")
            print(pm2_list)
    else:
        print_status("PM2: No instalado", 1)
    
    # Verificar NVM
    nvm_dir = os.path.expanduser("~/.nvm")
    if os.path.exists(nvm_dir):
        print_status("NVM: Instalado", 0)
        
        # Verificar versiones de Node.js instaladas con NVM
        nvm_versions = subprocess.getoutput("source ~/.bashrc && nvm list")
        if nvm_versions:
            print("Versiones de Node.js instaladas con NVM:")
            print(nvm_versions)
    else:
        print_status("NVM: No instalado", 1)
    
    print("=" * 50)

def create_ssh_user_with_sudo():
    """Crea usuarios SSH con opción de permisos sudo"""
    while True:
        choice = input("¿Quieres crear un usuario SSH adicional? (si/no): ").strip().lower()
        if choice in ['si', 's']:
            username = input("Ingrese el nombre del usuario: ").strip()
            password = getpass.getpass("Ingrese la contraseña para el usuario: ")
            
            # Crear usuario
            if run_command(f'sudo adduser --gecos "" --disabled-password {username}'):
                if run_command(f'echo "{username}:{password}" | sudo chpasswd'):
                    print_status(f"Usuario SSH {username} creado", 0)
                    
                    # Preguntar si necesita permisos sudo
                    sudo_choice = input(f"¿El usuario {username} requiere permisos sudo? (si/no): ").strip().lower()
                    if sudo_choice in ['si', 's']:
                        if run_command(f'sudo usermod -aG sudo {username}'):
                            print_status(f"Permisos sudo otorgados a {username}", 0)
                        else:
                            print_status(f"Error al otorgar permisos sudo a {username}", 1)
                    
                    # Crear directorio .ssh y configurar permisos
                    ssh_dir = f"/home/{username}/.ssh"
                    if run_command(f'sudo mkdir -p {ssh_dir}'):
                        if run_command(f'sudo chown {username}:{username} {ssh_dir}'):
                            if run_command(f'sudo chmod 700 {ssh_dir}'):
                                print_status(f"Directorio SSH configurado para {username}", 0)
                    
                    # Preguntar si quiere configurar clave SSH
                    ssh_key_choice = input(f"¿Quieres configurar una clave SSH para {username}? (si/no): ").strip().lower()
                    if ssh_key_choice in ['si', 's']:
                        configure_ssh_key(username)
                else:
                    print_status(f"Error al establecer contraseña para {username}", 1)
            else:
                print_status(f"Error al crear usuario SSH {username}", 1)
        elif choice in ['no', 'n']:
            break
        else:
            print("Por favor responda si o no.")

def configure_ssh_key(username):
    """Configura clave SSH para un usuario"""
    print("Opciones para configurar clave SSH:")
    print("1. Generar nueva clave SSH")
    print("2. Copiar clave SSH existente")
    print("3. Cancelar")
    
    choice = input("Seleccione una opción [1-3]: ").strip()
    
    if choice == '1':
        # Generar nueva clave
        key_type = input("Tipo de clave (rsa/ed25519) [ed25519]: ").strip() or "ed25519"
        key_comment = input("Comentario para la clave (ej. usuario@servidor): ").strip()
        
        if run_command(f'sudo -u {username} ssh-keygen -t {key_type} -C "{key_comment}" -f /home/{username}/.ssh/id_{key_type} -N ""'):
            print_status(f"Clave SSH {key_type} generada para {username}", 0)
            # Mostrar la clave pública
            pub_key_path = f"/home/{username}/.ssh/id_{key_type}.pub"
            if os.path.exists(pub_key_path):
                with open(pub_key_path, 'r') as f:
                    pub_key = f.read().strip()
                print(f"Clave pública generada:\n{pub_key}")
    
    elif choice == '2':
        # Copiar clave existente
        pub_key = input("Pegue la clave pública SSH: ").strip()
        authorized_keys_path = f"/home/{username}/.ssh/authorized_keys"
        
        with open(authorized_keys_path, 'w') as f:
            f.write(pub_key + '\n')
        
        if run_command(f'sudo chown {username}:{username} {authorized_keys_path}'):
            if run_command(f'sudo chmod 600 {authorized_keys_path}'):
                print_status(f"Clave SSH configurada para {username}", 0)

def install_fail2ban():
    """Instala y configura Fail2Ban"""
    print("Instalando Fail2Ban...")
    commands = [
        'sudo apt-get update',
        'sudo apt-get install -y fail2ban',
        'sudo systemctl start fail2ban',
        'sudo systemctl enable fail2ban'
    ]
    
    success = True
    for command in commands:
        if not run_command(command):
            success = False
            break
    
    if success:
        print_status("Fail2Ban instalado y configurado", 0)
        # Configurar jail básico para SSH
        configure_fail2ban_ssh()
    else:
        print_status("Error al instalar Fail2Ban", 1)

def configure_fail2ban_ssh():
    """Configura Fail2Ban para proteger SSH"""
    jail_config = """[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
"""
    
    with open('/etc/fail2ban/jail.local', 'w') as f:
        f.write(jail_config)
    
    if run_command('sudo systemctl restart fail2ban'):
        print_status("Fail2Ban configurado para proteger SSH", 0)

def install_ufw():
    """Instala y configura UFW (Uncomplicated Firewall)"""
    print("Instalando y configurando UFW...")
    commands = [
        'sudo apt-get update',
        'sudo apt-get install -y ufw',
        'sudo ufw --force reset',
        'sudo ufw default deny incoming',
        'sudo ufw default allow outgoing',
        'sudo ufw allow ssh',
        'sudo ufw allow 80/tcp',
        'sudo ufw allow 443/tcp',
        'sudo ufw --force enable'
    ]
    
    success = True
    for command in commands:
        if not run_command(command):
            success = False
            break
    
    if success:
        print_status("UFW instalado y configurado", 0)
        print("Puertos abiertos: SSH (22), HTTP (80), HTTPS (443)")
    else:
        print_status("Error al instalar UFW", 1)

def install_certbot():
    """Instala Certbot para certificados SSL/TLS"""
    print("Instalando Certbot...")
    commands = [
        'sudo apt-get update',
        'sudo apt-get install -y certbot python3-certbot-nginx',
        'sudo apt-get install -y certbot python3-certbot-apache'
    ]
    
    success = True
    for command in commands:
        if not run_command(command):
            success = False
            break
    
    if success:
        print_status("Certbot instalado", 0)
        print("Para obtener un certificado SSL:")
        print("sudo certbot --nginx -d tu-dominio.com")
        print("sudo certbot --apache -d tu-dominio.com")
    else:
        print_status("Error al instalar Certbot", 1)

def install_common_services():
    """Instala servicios comunes útiles"""
    print("Instalando servicios comunes...")
    services = [
        'htop', 'vim', 'wget', 'curl', 'unzip', 'zip', 'tree', 
        'net-tools', 'nmap', 'tcpdump', 'iotop', 'ncdu', 'rsync'
    ]
    
    success = True
    for i, service in enumerate(services, 1):
        if run_command(f'sudo apt-get install -y {service}'):
            print_status(f"{service} instalado", 0, i, len(services))
        else:
            print_status(f"Error al instalar {service}", 1)
            success = False
    
    if success:
        print_status("Servicios comunes instalados", 0)

def configure_swap():
    """Configura memoria swap"""
    print("Configurando memoria swap...")
    
    # Verificar si ya existe swap
    swap_check = subprocess.getoutput('swapon --show')
    if swap_check:
        print("Ya existe memoria swap configurada:")
        print(swap_check)
        choice = input("¿Quieres reconfigurar el swap? (si/no): ").strip().lower()
        if choice not in ['si', 's']:
            return
    
    # Obtener tamaño de RAM
    ram_size = int(subprocess.getoutput("grep MemTotal /proc/meminfo | awk '{print $2}'")) // 1024  # MB
    swap_size = min(ram_size * 2, 8192)  # 2x RAM o máximo 8GB
    
    print(f"RAM detectada: {ram_size} MB")
    print(f"Tamaño de swap recomendado: {swap_size} MB")
    
    custom_size = input(f"Ingrese el tamaño del swap en MB (Enter para {swap_size}): ").strip()
    if custom_size:
        try:
            swap_size = int(custom_size)
        except ValueError:
            print("Tamaño inválido, usando valor por defecto")
    
    commands = [
        f'sudo fallocate -l {swap_size}M /swapfile',
        'sudo chmod 600 /swapfile',
        'sudo mkswap /swapfile',
        'sudo swapon /swapfile',
        'echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab'
    ]
    
    success = True
    for command in commands:
        if not run_command(command):
            success = False
            break
    
    if success:
        print_status(f"Swap configurado ({swap_size} MB)", 0)
    else:
        print_status("Error al configurar swap", 1)

def optimize_system():
    """Optimiza el sistema"""
    print("Optimizando sistema...")
    
    # Optimizar parámetros del kernel
    sysctl_config = """# Optimizaciones del sistema
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_max_tw_buckets = 2000000
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65535
"""
    
    with open('/etc/sysctl.conf', 'a') as f:
        f.write(sysctl_config)
    
    if run_command('sudo sysctl -p'):
        print_status("Parámetros del kernel optimizados", 0)
    
    # Optimizar límites del sistema
    limits_config = """# Límites del sistema optimizados
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
root soft nofile 65535
root hard nofile 65535
"""
    
    with open('/etc/security/limits.conf', 'a') as f:
        f.write(limits_config)
    
    print_status("Límites del sistema optimizados", 0)

def install_monitoring_tools():
    """Instala herramientas de monitoreo"""
    print("Instalando herramientas de monitoreo...")
    
    tools = [
        'htop', 'iotop', 'ncdu', 'nethogs', 'iftop', 'glances'
    ]
    
    success = True
    for tool in tools:
        if run_command(f'sudo apt-get install -y {tool}'):
            print_status(f"{tool} instalado", 0)
        else:
            print_status(f"Error al instalar {tool}", 1)
            success = False
    
    if success:
        print_status("Herramientas de monitoreo instaladas", 0)

def create_docker_compose_template():
    """Crea plantillas de Docker Compose comunes"""
    print("Creando plantillas de Docker Compose...")
    
    templates = {
        'nginx': """version: '3.8'
services:
  nginx:
    image: nginx:latest
    container_name: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    restart: unless-stopped
""",
        'wordpress': """version: '3.8'
services:
  wordpress:
    image: wordpress:latest
    container_name: wordpress
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress_password
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wordpress_data:/var/www/html
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: mysql:5.7
    container_name: wordpress_db
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress_password
      MYSQL_ROOT_PASSWORD: somewordpress
    volumes:
      - db_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  wordpress_data:
  db_data:
""",
        'nextcloud': """version: '3.8'
services:
  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    ports:
      - "8080:80"
    environment:
      MYSQL_HOST: db
      MYSQL_DATABASE: nextcloud
      MYSQL_USER: nextcloud
      MYSQL_PASSWORD: nextcloud_password
    volumes:
      - nextcloud_data:/var/www/html
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: mariadb:10.6
    container_name: nextcloud_db
    environment:
      MYSQL_DATABASE: nextcloud
      MYSQL_USER: nextcloud
      MYSQL_PASSWORD: nextcloud_password
      MYSQL_ROOT_PASSWORD: somewordpress
    volumes:
      - db_data:/var/lib/mysql
    restart: unless-stopped

volumes:
  nextcloud_data:
  db_data:
"""
    }
    
    for name, template in templates.items():
        filename = f"docker-compose-{name}.yml"
        with open(filename, 'w') as f:
            f.write(template)
        print_status(f"Plantilla {filename} creada", 0)
    
    print("Plantillas creadas en el directorio actual")

def backup_system():
    """Crea un backup del sistema"""
    print("Creando backup del sistema...")
    
    backup_dir = f"/backup/system-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    if run_command(f'sudo mkdir -p {backup_dir}'):
        # Backup de configuraciones importantes
        important_dirs = [
            '/etc/nginx',
            '/etc/mysql',
            '/etc/ssh',
            '/etc/fail2ban',
            '/etc/ufw',
            '/var/www'
        ]
        
        for dir_path in important_dirs:
            if os.path.exists(dir_path):
                backup_path = f"{backup_dir}{dir_path}"
                if run_command(f'sudo mkdir -p {os.path.dirname(backup_path)}'):
                    if run_command(f'sudo cp -r {dir_path} {backup_path}'):
                        print_status(f"Backup de {dir_path}", 0)
        
        # Backup de bases de datos
        if run_command('which mysql'):
            if run_command(f'sudo mysqldump --all-databases > {backup_dir}/all_databases.sql'):
                print_status("Backup de bases de datos MySQL", 0)
        
        print_status(f"Backup completado en {backup_dir}", 0)
    else:
        print_status("Error al crear directorio de backup", 1)

def manage_elasticsearch_indices():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("      Submenú de Gestión de Índices Elasticsearch")
        print("--------------------------------------------------")
        print("1. Listar índices de Elasticsearch")
        print("2. Cambiar número de réplicas de índices (uno o todos)")
        print("3. Volver al menú principal")
        print("--------------------------------------------------")
        choice = input("Seleccione una opción [1-3]: ").strip()

        if choice == '1':
            list_elasticsearch_indices()  # Función existente para listar índices (puedes actualizarla según tu necesidad)
        elif choice == '2':
            advanced_manage_elasticsearch_indices()  # Función avanzada para gestionar réplicas de índices
        elif choice == '3':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def advanced_manage_elasticsearch_indices():
    # Solicitar si se está usando SSL
    use_ssl = input("¿Está utilizando SSL para conectarse a Elasticsearch? (si/no): ").strip().lower()
    protocol = "https" if use_ssl in ['si', 's'] else "http"

    # Solicitar credenciales
    es_host = input("Ingrese el host de Elasticsearch (ej. localhost:9200): ").strip()
    es_user = input("Ingrese el nombre de usuario de Elasticsearch: ").strip()
    es_password = getpass.getpass("Ingrese la contraseña de Elasticsearch: ")

    # Listar índices
    command = f'curl -k -u {es_user}:{es_password} -X GET "{protocol}://{es_host}/_cat/indices?v&s=store.size:desc"'
    indices_output = subprocess.getoutput(command)
    print("Índices en Elasticsearch:")
    print(indices_output)

    # Procesar la salida para mostrar los índices
    indices_lines = indices_output.split('\n')
    if len(indices_lines) > 1:
        headers = indices_lines[0]
        indices = indices_lines[1:]
        print(headers)
        for idx, line in enumerate(indices, start=1):
            print(f"{idx}. {line.split()[2]}")

        print(f"{len(indices) + 1}. Cambiar réplicas en todos los índices")
        print(f"{len(indices) + 2}. Volver al menú principal")

        while True:
            choice = input("Seleccione una opción: ").strip()
            if choice.isdigit():
                choice = int(choice)

                # Opción para modificar un índice individual
                if 1 <= choice <= len(indices):
                    index_name = indices[choice - 1].split()[2]
                    replicas = input(f"Ingrese el nuevo número de réplicas para el índice {index_name}: ").strip()
                    update_command = f'curl -X PUT "{protocol}://{es_host}/{index_name}/_settings" -H \'Content-Type: application/json\' -d\'{{"index": {{"number_of_replicas": {replicas}}}}}\' -u {es_user}:{es_password} -k'
                    result = subprocess.getoutput(update_command)
                    print(result)

                # Opción para modificar todos los índices
                elif choice == len(indices) + 1:
                    replicas = input("Ingrese el nuevo número de réplicas para todos los índices: ").strip()
                    update_command = f'curl -X PUT "{protocol}://{es_host}/*/_settings" -H \'Content-Type: application/json\' -d\'{{"index": {{"number_of_replicas": {replicas}}}}}\' -u {es_user}:{es_password} -k'
                    result = subprocess.getoutput(update_command)
                    print(result)

                # Volver al menú principal
                elif choice == len(indices) + 2:
                    break
                else:
                    print("Selección inválida.")
            else:
                print("Selección inválida.")
    else:
        print("No se encontraron índices.")
        
def update_script():
    repo_url = "https://github.com/De0xyS3/menu_scripts"
    script_path = "/tmp/menu.py"
    current_script_path = "/usr/local/bin/menu"

    # Clonar o actualizar el repositorio
    if not os.path.isdir("/tmp/menu_scripts"):
        subprocess.run(["git", "clone", repo_url, "/tmp/menu_scripts"], check=True)
    else:
        subprocess.run(["git", "-C", "/tmp/menu_scripts", "pull"], check=True)

    # Copiar el script actualizado
    shutil.copyfile(f"/tmp/menu_scripts/main/menu.py", script_path)
    shutil.copyfile(script_path, current_script_path)
    print_status("Script actualizado. Por favor, vuelva a ejecutar el script.", 0)
    exit()

def check_for_updates():
    repo_url = "https://github.com/De0xyS3/menu_scripts"
    if not os.path.isdir("/tmp/menu_scripts"):
        subprocess.run(["git", "clone", repo_url, "/tmp/menu_scripts"], check=True)
    else:
        subprocess.run(["git", "-C", "/tmp/menu_scripts", "pull"], check=True)

def list_elasticsearch_indices():
    # Solicitar si se está usando SSL
    use_ssl = input("¿Está utilizando SSL para conectarse a Elasticsearch? (si/no): ").strip().lower()
    protocol = "https" if use_ssl in ['si', 's'] else "http"
    
    # Solicitar credenciales
    es_host = input("Ingrese el host de Elasticsearch (ej. localhost:9200): ").strip()
    es_user = input("Ingrese el nombre de usuario de Elasticsearch: ").strip()
    es_password = getpass.getpass("Ingrese la contraseña de Elasticsearch: ")

    # Listar índices
    command = f'curl -k -u {es_user}:{es_password} -X GET "{protocol}://{es_host}/_cat/indices?v&s=store.size:desc"'
    indices_output = subprocess.getoutput(command)
    print("Índices en Elasticsearch:")
    print(indices_output)

    # Procesar la salida para mostrar los índices y permitir al usuario seleccionar cuál eliminar
    indices_lines = indices_output.split('\n')
    if len(indices_lines) > 1:
        headers = indices_lines[0]
        indices = indices_lines[1:]
        print(headers)
        for idx, line in enumerate(indices, start=1):
            print(f"{idx}. {line}")

        print(f"{len(indices) + 1}. Volver al menú principal")

        while True:
            choice = input("Seleccione un índice para eliminar por número: ").strip()
            if choice.isdigit():
                choice = int(choice)
                if choice == len(indices) + 1:
                    break
                elif 1 <= choice <= len(indices):
                    index_name = indices[choice - 1].split()[2]
                    confirm = input(f"¿Está seguro de que desea eliminar el índice {index_name}? (si/no): ").strip().lower()
                    if confirm in ['si', 's']:
                        delete_command = f'curl -k -u {es_user}:{es_password} -X DELETE "{protocol}://{es_host}/{index_name}"'
                        if run_command(delete_command):
                            print_status(f"Índice {index_name} eliminado con éxito", 0)
                        else:
                            print_status(f"Error al eliminar el índice {index_name}", 1)
                    else:
                        print("Operación cancelada.")
                else:
                    print("Selección inválida.")
            else:
                print("Selección inválida.")
    else:
        print("No se encontraron índices.")

def deploy_selenium():
    # Verificar si Docker está instalado
    if subprocess.call(["which", "docker"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print_status("Docker no está instalado. Por favor, instálalo primero.", 1)
        return

    # Pedir al usuario el secreto para el visor VNC de Selenium
    selenium_secret = getpass.getpass("Ingrese el secret para Selenium: ")

    # Comando para ejecutar el contenedor Selenium Hub
    hub_command = f'docker run -d --name selenium-hub -p 4444:4444 selenium/hub'
    # Comando para ejecutar el contenedor Selenium Node Firefox con el secret para el visor VNC
    node_command = f'docker run -d --name selenium-firefox --link selenium-hub:hub -e SE_EVENT_BUS_HOST=hub -e SE_EVENT_BUS_PUBLISH_PORT=4442 -e SE_EVENT_BUS_SUBSCRIBE_PORT=4443 -e SE_OPTS="-Dwebdriver.chrome.driver=/usr/local/bin/chromedriver -Dwebdriver.gecko.driver=/usr/local/bin/geckodriver -Dwebdriver.chrome.logfile=/tmp/chromedriver.log -Dwebdriver.gecko.logfile=/tmp/geckodriver.log -Dwebdriver.chrome.verboseLogging=true -Dwebdriver.gecko.verboseLogging=true -Dwebdriver.vnc.password={selenium_secret}" selenium/node-firefox'

    print_status("Desplegando Selenium Hub...", subprocess.call(hub_command, shell=True))
    print_status("Desplegando Selenium Node Firefox...", subprocess.call(node_command, shell=True))

def configure_ssh_logging_for_user(user):
    log_dir = f"/var/log/ssh_commands/{user}"
    log_file = f"{log_dir}/ssh_commands_{user}_$(date +%Y%m%d).log"
    monitor_dir = f"/home/{user}/monitoring"

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        os.chmod(log_dir, 0o777)
    
    os.system(f'touch {log_file}')
    os.chmod(log_file, 0o666)

    profile_path = f"/home/{user}/.profile"
    log_script = f"""
# Monitoreo de comandos SSH para {user}
LOG_DIR={log_dir}
LOG_FILE="{log_file}"

# Crear el archivo de registro si no existe
touch "${{LOG_FILE}}"

# Permisos de escritura para el archivo de registro
chmod 666 "${{LOG_FILE}}"

# Agregar la hora del inicio de sesión y el usuario al archivo de registro
echo "Sesión iniciada por el usuario $(whoami) en $(date)" | sudo tee -a "${{LOG_FILE}}"
echo "------------------------------------------------------------" | sudo tee -a "${{LOG_FILE}}"

# Registrar los comandos ejecutados en el archivo de registro
PROMPT_COMMAND='echo "$(date "+%Y-%m-%d %T") $(whoami) $(history 1)" | sudo tee -a "${{LOG_FILE}}"'
echo "------------------------------------------------------------" | sudo tee -a "${{LOG_FILE}}"
"""

    with open(profile_path, 'a') as f:
        f.write(log_script)

    os.makedirs(monitor_dir, exist_ok=True)
    symlink_path = f"{monitor_dir}/ssh_commands.log"
    if os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(log_file, symlink_path)
    os.chmod(symlink_path, 0o777)
    
    print_status(f"Monitoreo SSH configurado para {user}", 0)

def configure_ssh_logging():
    if not is_root():
        print("Este script debe ejecutarse como root o utilizando sudo.")
        return

    while True:
        users = get_all_users()
        print("Usuarios del sistema:")
        for idx, user in enumerate(users, start=1):
            print(f"{idx}. {user}")
        print(f"{len(users) + 1}. Volver al menú principal")
        
        user_choice = input("Seleccione un usuario por número: ").strip()
        if user_choice.isdigit():
            user_choice = int(user_choice)
            if user_choice == len(users) + 1:
                break
            elif 1 <= user_choice <= len(users):
                user = users[user_choice - 1]
                configure_ssh_logging_for_user(user)
            else:
                print("Selección inválida.")
        else:
            print("Selección inválida.")

def run_command(command):
    result = os.system(command + " > /dev/null 2>&1")
    return result == 0

def configure_multipathd():
    print("Configurando multipathd...")
    if run_command('sudo apt-get update') and run_command('sudo apt-get install -y multipath-tools') and run_command('sudo systemctl restart multipathd') and run_command('sudo multipath -F') and run_command('sudo multipath -v2'):
        with open('/etc/multipath.conf', 'w') as f:
            f.write("""
defaults {
    user_friendly_names yes
    find_multipaths yes
}

blacklist {
    devnode "^sda$"
}

devices {
    device {
        vendor ".*"
        product ".*"
        path_grouping_policy "multibus"
        getuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"
        path_selector "round-robin 0"
        path_checker "readsector0"
        features "1 queue_if_no_path"
        hardware_handler "0"
        prio "const"
        failback "immediate"
    }
}
""")
        if run_command('sudo systemctl restart multipathd'):
            print_status("Multipathd configurado", 0)
        else:
            print_status("Error al configurar multipathd", 1)
    else:
        print_status("Error al configurar multipathd", 1)

def configure_timezone():
    print("Configurando zona horaria a America/Lima...")
    if run_command('sudo timedatectl set-timezone America/Lima'):
        print_status("Zona horaria configurada a America/Lima", 0)
    else:
        print_status("Error al configurar zona horaria", 1)

def create_ssh_users():
    """Función legacy - redirige a la nueva función mejorada"""
    create_ssh_user_with_sudo()

def list_available_versions(package_name):
    result = subprocess.getoutput(f'apt-cache madison {package_name}')
    versions = [line.split('|')[1].strip() for line in result.split('\n')]
    return versions

def select_version(package_name):
    versions = list_available_versions(package_name)
    if versions:
        print(f"Versiones disponibles para {package_name}:")
        for idx, version in enumerate(versions, start=1):
            print(f"{idx}. {version}")
        print(f"{len(versions) + 1}. Volver al menú anterior")

        choice = input(f"Seleccione una versión para instalar {package_name}: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if choice == len(versions) + 1:
                return None
            elif 1 <= choice <= len(versions):
                return versions[choice - 1]
            else:
                print("Selección inválida.")
        else:
            print("Selección inválida.")
    else:
        print(f"No hay versiones disponibles para {package_name}.")
    return None

def install_mysql():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Instalación MySQL")
        print("--------------------------------------------------")
        print("1. Instalar MySQL y eliminar datos de prueba")
        print("2. Volver al menú anterior")
        print("--------------------------------------------------")
        mysql_choice = input("Seleccione una opción [1-2]: ").strip()
        if mysql_choice == '1':
            version = select_version("mysql-server")
            if version:
                if run_command(f'sudo apt-get update') and run_command(f'sudo apt-get install -y mysql-server={version}'):
                    print_status("MySQL instalado", 0)
                    mysql_root_password = getpass.getpass("Ingrese la contraseña para el usuario root de MySQL: ")
                    if run_command(f'sudo mysql -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED WITH mysql_native_password BY \'{mysql_root_password}\';"') and run_command('sudo mysql -e "FLUSH PRIVILEGES;"') and run_command('sudo mysql -e "DELETE FROM mysql.user WHERE User=\'\';"') and run_command('sudo mysql -e "DROP DATABASE IF EXISTS test;"') and run_command('sudo mysql -e "DELETE FROM mysql.db WHERE Db=\'test\' OR Db=\'test\\_%\';"') and run_command('sudo mysql -e "FLUSH PRIVILEGES;"'):
                        print_status("MySQL configurado y datos de prueba eliminados", 0)
                    else:
                        print_status("Error al configurar MySQL", 1)
                else:
                    print_status("Error al instalar MySQL", 1)
        elif mysql_choice == '2':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def create_mysql_users():
    mysql_root_password = getpass.getpass("Ingrese la contraseña para el usuario root de MySQL: ")
    while True:
        user_choice = input("¿Quieres crear un usuario MySQL adicional? (si/no): ").strip().lower()
        if user_choice in ['si', 's']:
            mysql_user = input("Ingrese el nombre del usuario MySQL: ").strip()
            mysql_password = getpass.getpass("Ingrese la contraseña para el usuario MySQL: ")
            if run_command(f'sudo mysql -u root -p{mysql_root_password} -e "CREATE USER \'{mysql_user}\'@\'%\' IDENTIFIED BY \'{mysql_password}\';"'):
                print_status(f"Usuario MySQL {mysql_user} creado", 0)
            else:
                print_status(f"Error al crear usuario MySQL {mysql_user}", 1)
        elif user_choice in ['no', 'n']:
            break
        else:
            print("Por favor responda si o no.")

def enable_mysql_remote():
    mysql_root_password = getpass.getpass("Ingrese la contraseña para el usuario root de MySQL: ")
    if run_command('sudo sed -i "s/^bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf') and run_command('sudo systemctl restart mysql'):
        print_status("Conexión remota de MySQL habilitada", 0)
    else:
        print_status("Error al habilitar conexión remota de MySQL", 1)

def grant_mysql_permissions():
    mysql_root_password = getpass.getpass("Ingrese la contraseña para el usuario root de MySQL: ")
    users = subprocess.getoutput(f'mysql -u root -p{mysql_root_password} -e "SELECT User FROM mysql.user WHERE User != \'root\' AND Host != \'localhost\';"')
    users = users.split('\n')[1:]  # Remove header
    print("Usuarios MySQL existentes:")
    for idx, user in enumerate(users, start=1):
        print(f"{idx}. {user.strip()}")
    
    user_choice = input("Seleccione un usuario por número: ").strip()
    if not user_choice.isdigit() or int(user_choice) < 1 or int(user_choice) > len(users):
        print("Selección inválida.")
        return

    mysql_user = users[int(user_choice) - 1].strip()
    if run_command(f'sudo mysql -u root -p{mysql_root_password} -e "GRANT ALL PRIVILEGES ON *.* TO \'{mysql_user}\'@\'%\' WITH GRANT OPTION;"') and run_command(f'sudo mysql -u root -p{mysql_root_password} -e "FLUSH PRIVILEGES;"'):
        print_status(f"Permisos otorgados a {mysql_user}", 0)
    else:
        print_status(f"Error al otorgar permisos a {mysql_user}", 1)

def mysql_submenu():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Configuración MySQL")
        print("--------------------------------------------------")
        print("1. Instalar MySQL y eliminar datos de prueba")
        print("2. Crear usuarios MySQL")
        print("3. Permitir conexión remota en MySQL")
        print("4. Asignar permisos a usuarios MySQL")
        print("5. Volver al menú principal")
        print("--------------------------------------------------")
        mysql_choice = input("Seleccione una opción [1-5]: ").strip()
        if mysql_choice == '1':
            install_mysql()
        elif mysql_choice == '2':
            create_mysql_users()
        elif mysql_choice == '3':
            enable_mysql_remote()
        elif mysql_choice == '4':
            grant_mysql_permissions()
        elif mysql_choice == '5':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def install_mariadb():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Instalación MariaDB")
        print("--------------------------------------------------")
        print("1. Instalar MariaDB y eliminar datos de prueba")
        print("2. Volver al menú anterior")
        print("--------------------------------------------------")
        mariadb_choice = input("Seleccione una opción [1-2]: ").strip()
        if mariadb_choice == '1':
            version = select_version("mariadb-server")
            if version:
                if run_command(f'sudo apt-get update') and run_command(f'sudo apt-get install -y mariadb-server={version}'):
                    print_status("MariaDB instalado", 0)
                    mariadb_root_password = getpass.getpass("Ingrese la contraseña para el usuario root de MariaDB: ")
                    if run_command(f'sudo mysql -e "ALTER USER \'root\'@\'localhost\' IDENTIFIED BY \'{mariadb_root_password}\';"') and run_command('sudo mysql -e "FLUSH PRIVILEGES;"') and run_command('sudo mysql -e "DELETE FROM mysql.user WHERE User=\'\';"') and run_command('sudo mysql -e "DROP DATABASE IF EXISTS test;"') and run_command('sudo mysql -e "DELETE FROM mysql.db WHERE Db=\'test\' OR Db=\'test\\_%\';"') and run_command('sudo mysql -e "FLUSH PRIVILEGES;"'):
                        print_status("MariaDB configurado y datos de prueba eliminados", 0)
                    else:
                        print_status("Error al configurar MariaDB", 1)
                else:
                    print_status("Error al instalar MariaDB", 1)
        elif mariadb_choice == '2':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def install_docker():
    """Función legacy - redirige a la nueva función mejorada"""
    install_docker_improved()

def install_nginx():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Instalación Nginx")
        print("--------------------------------------------------")
        print("1. Instalar Nginx")
        print("2. Volver al menú anterior")
        print("--------------------------------------------------")
        nginx_choice = input("Seleccione una opción [1-2]: ").strip()
        if nginx_choice == '1':
            version = select_version("nginx")
            if version:
                if run_command(f'sudo apt-get update') and run_command(f'sudo apt-get install -y nginx={version}') and run_command('sudo systemctl start nginx') and run_command('sudo systemctl enable nginx'):
                    print_status("Nginx instalado", 0)
                else:
                    print_status("Error al instalar Nginx", 1)
        elif nginx_choice == '2':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def install_php():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Instalación PHP")
        print("--------------------------------------------------")
        print("1. Instalar PHP")
        print("2. Volver al menú anterior")
        print("--------------------------------------------------")
        php_choice = input("Seleccione una opción [1-2]: ").strip()
        if php_choice == '1':
            version = select_version("php")
            if version:
                if run_command(f'sudo apt-get update') and run_command(f'sudo apt-get install -y php={version} php-cli php-fpm php-json php-common php-mysql php-zip php-gd php-mbstring php-curl php-xml php-bcmath php-json'):
                    print_status("PHP y módulos instalados", 0)
                else:
                    print_status("Error al instalar PHP", 1)
        elif php_choice == '2':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def install_laravel():
    print("Instalando Laravel...")
    if run_command('sudo apt-get update') and run_command('sudo apt-get install -y curl php-cli php-mbstring unzip') and run_command('curl -sS https://getcomposer.org/installer | php') and run_command('sudo mv composer.phar /usr/local/bin/composer') and run_command('composer global require laravel/installer') and run_command('echo "export PATH=$PATH:$HOME/.config/composer/vendor/bin" >> ~/.bashrc') and run_command('source ~/.bashrc'):
        print_status("Laravel instalado", 0)
    else:
        print_status("Error al instalar Laravel", 1)

def expand_disk():
    print("Expandiendo disco...")
    if run_command('sudo apt-get update') and run_command('sudo apt-get install -y cloud-guest-utils') and run_command('sudo growpart /dev/sda 1'):
        print_status("Partición del disco expandida", 0)
        if run_command('sudo resize2fs /dev/sda1'):
            print_status("Sistema de archivos expandido", 0)
        else:
            print_status("Error al expandir el sistema de archivos", 1)
    else:
        print_status("Error al expandir la partición del disco", 1)

def install_git():
    print("Instalando Git...")
    if run_command('sudo apt-get update') and run_command('sudo apt-get install -y git'):
        print_status("Git instalado", 0)
    else:
        print_status("Error al instalar Git", 1)

def configure_cronjob():
    print("Configurando cronjob...")
    print("Recomendaciones de comandos para optimizar el sistema:")
    print("1. echo 3 > /proc/sys/vm/drop_caches")
    print("2. sync; echo 3 > /proc/sys/vm/drop_caches")
    print("3. sysctl -w vm.drop_caches=3")
    print("4. /sbin/sysctl -w vm.drop_caches=3")
    command = input("Ingrese el comando a usar para el cronjob: ").strip()
    schedule = input("Ingrese el tiempo de ejecución del cronjob (ej. '0 3 * * *' para cada día a las 3am): ").strip()
    
    cron_job = f"{schedule} {command}"
    with open("/etc/cron.d/optimize_system", "w") as cron_file:
        cron_file.write(cron_job + "\n")
    
    run_command("sudo systemctl restart cron")
    print_status("Cronjob configurado", 0)

def list_interfaces():
    interfaces = os.listdir('/sys/class/net/')
    return [iface for iface in interfaces if iface != 'lo']

def get_ip_info(interface):
    ip_info = {}
    ip_output = subprocess.getoutput(f"ip a show {interface}")
    ip_lines = ip_output.splitlines()
    for line in ip_lines:
        if "inet " in line:
            parts = line.split()
            ip_info['ip'] = parts[1]  # IP and netmask
            break
    return ip_info

def get_gateway_info():
    gateway_output = subprocess.getoutput("ip route | grep default")
    parts = gateway_output.split()
    gateway = parts[2]  # Gateway is the 3rd element in the output
    return gateway

def configure_static_ip():
    while True:
        interfaces = list_interfaces()
        print("Interfaces disponibles:")
        for idx, iface in enumerate(interfaces, start=1):
            print(f"{idx}. {iface}")
        print(f"{len(interfaces) + 1}. Volver al menú anterior")
        
        iface_choice = input("Seleccione una interfaz por número: ").strip()
        if iface_choice.isdigit() and 1 <= int(iface_choice) <= len(interfaces):
            interface = interfaces[int(iface_choice) - 1]
            ip_info = get_ip_info(interface)
            gateway = get_gateway_info()
            configure_static_ip(interface, ip_info, gateway)
            break
        elif iface_choice == str(len(interfaces) + 1):
            break
        else:
            print("Selección inválida.")

def check_netplan_config(interface):
    netplan_dir = "/etc/netplan/"
    config_files = os.listdir(netplan_dir)
    for file in config_files:
        with open(os.path.join(netplan_dir, file), 'r') as f:
            config = yaml.safe_load(f)
            if "ethernets" in config.get("network", {}):
                if interface in config["network"]["ethernets"]:
                    return config["network"]["ethernets"][interface]
    return None

def check_interfaces_config(interface):
    config_file = "/etc/network/interfaces"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith(f"iface {interface} inet"):
                return lines[i:i+3]  # Assuming max 3 lines per interface
    return None

def configure_virtual_ip():
    interfaces = list_interfaces()
    print("Interfaces disponibles:")
    for idx, iface in enumerate(interfaces, start=1):
        print(f"{idx}. {iface}")
    iface_choice = input("Seleccione una interfaz por número: ").strip()
    if iface_choice.isdigit() and 1 <= int(iface_choice) <= len(interfaces):
        interface = interfaces[int(iface_choice) - 1]

        # Check configuration using Netplan or interfaces
        config = check_netplan_config(interface)
        if not config:
            config = check_interfaces_config(interface)

        if config:
            if 'dhcp4' in config and config['dhcp4']:
                print(f"La interfaz {interface} está configurada con DHCP.")
                set_static = input("¿Desea configurar esta IP como estática en Netplan para agregar una IP virtual? (si/no): ").strip().lower()
                if set_static in ['si', 's']:
                    configure_static_ip(interface)
                else:
                    print("No se puede configurar una IP virtual en una interfaz con DHCP.")
                    return
            else:
                print(f"La interfaz {interface} está configurada con una IP estática.")
        else:
            print(f"No se encontró configuración para la interfaz {interface}.")

        ip_address = input("Ingrese la IP virtual (ej. 10.10.10.2/24): ").strip()

        netplan_config_path = f"/etc/netplan/{interface}.yaml"
        with open(netplan_config_path, "r") as file:
            config_content = yaml.safe_load(file)

        config_content["network"]["ethernets"][interface].setdefault("addresses", []).append(ip_address)

        with open(netplan_config_path, "w") as file:
            yaml.dump(config_content, file, default_flow_style=False)

        print_status(f"Configuración de IP virtual {ip_address} agregada para {interface}", 0)
        subprocess.run(["sudo", "netplan", "apply"], check=True)
        print_status(f"IP virtual {ip_address} activada en {interface}", 0)
    else:
        print("Selección inválida.")

def configure_dhcp():
    while True:
        interfaces = list_interfaces()
        print("Interfaces disponibles:")
        for idx, iface in enumerate(interfaces, start=1):
            print(f"{idx}. {iface}")
        print(f"{len(interfaces) + 1}. Volver al menú anterior")
        
        iface_choice = input("Seleccione una interfaz por número: ").strip()
        if iface_choice.isdigit() and 1 <= int(iface_choice) <= len(interfaces):
            interface = interfaces[int(iface_choice) - 1]

            config_lines = [
                f"auto {interface}",
                f"iface {interface} inet dhcp"
            ]

            with open(f"/etc/network/interfaces.d/{interface}", "w") as config_file:
                config_file.write("\n".join(config_lines) + "\n")

            print_status(f"Configuración DHCP agregada para {interface}", 0)
            subprocess.run(["sudo", "ifdown", interface], check=True)
            subprocess.run(["sudo", "ifup", interface], check=True)
            print_status(f"DHCP activado en {interface}", 0)
            break
        elif iface_choice == str(len(interfaces) + 1):
            break
        else:
            print("Selección inválida.")

def configure_new_disk():
    print("Configurando nuevo disco...")
    while True:
        disks = subprocess.getoutput("lsblk -dn -o NAME,SIZE").splitlines()
        print("Discos disponibles:")
        for idx, disk in enumerate(disks, start=1):
            print(f"{idx}. {disk}")
        print(f"{len(disks) + 1}. Volver al menú anterior")

        choice = input("Seleccione un disco por número: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(disks):
            disk = disks[int(choice) - 1].split()[0]
            mount_point = input("Ingrese el punto de montaje (ej. /mnt/nuevo_disco): ").strip()

            # Crear partición, formatear y montar el disco
            subprocess.run(["sudo", "parted", f"/dev/{disk}", "mklabel", "gpt"], check=True)
            subprocess.run(["sudo", "parted", f"/dev/{disk}", "mkpart", "primary", "ext4", "0%", "100%"], check=True)
            subprocess.run(["sudo", "mkfs.ext4", f"/dev/{disk}1"], check=True)
            subprocess.run(["sudo", "mkdir", "-p", mount_point], check=True)
            subprocess.run(["sudo", "mount", f"/dev/{disk}1", mount_point], check=True)

            # Agregar a /etc/fstab
            with open("/etc/fstab", "a") as fstab:
                fstab.write(f"/dev/{disk}1 {mount_point} ext4 defaults 0 0\n")

            print_status(f"Disco /dev/{disk} configurado y montado en {mount_point}", 0)
            break
        elif choice == str(len(disks) + 1):
            break
        else:
            print("Selección inválida.")

def network_submenu():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Configuración de Red")
        print("--------------------------------------------------")
        print("1. Configurar IP estática")
        print("2. Configurar DHCP")
        print("3. Configurar IP virtual")
        print("4. Volver al menú principal")
        print("--------------------------------------------------")
        network_choice = input("Seleccione una opción [1-4]: ").strip()
        if network_choice == '1':
            configure_static_ip()
        elif network_choice == '2':
            configure_dhcp()
        elif network_choice == '3':
            configure_virtual_ip()
        elif network_choice == '4':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")
        

def docker_submenu():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Contenedores Docker")
        print("--------------------------------------------------")
        print("1. Desplegar Selenium")
        print("2. Volver al menú principal")
        print("--------------------------------------------------")
        docker_choice = input("Seleccione una opción [1-2]: ").strip()
        if docker_choice == '1':
            deploy_selenium()
        elif docker_choice == '2':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def configure_samba():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Configuración Samba")
        print("--------------------------------------------------")
        print("1. Instalar Samba")
        print("2. Publicar carpeta compartida")
        print("3. Establecer permisos para la carpeta")
        print("4. Volver al menú principal")
        print("--------------------------------------------------")
        samba_choice = input("Seleccione una opción [1-4]: ").strip()
        if samba_choice == '1':
            install_samba()
        elif samba_choice == '2':
            share_folder_samba()
        elif samba_choice == '3':
            set_samba_permissions()
        elif samba_choice == '4':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def install_samba():
    print("Instalando Samba...")
    if run_command('sudo apt-get update') and run_command('sudo apt-get install -y samba'):
        print_status("Samba instalado", 0)
    else:
        print_status("Error al instalar Samba", 1)

def share_folder_samba():
    folder_to_share = input("Ingrese la ruta completa de la carpeta a compartir: ").strip()
    share_name = input("Ingrese el nombre para la carpeta compartida: ").strip()

    with open('/etc/samba/smb.conf', 'a') as smb_conf:
        smb_conf.write(f"""
[{share_name}]
   path = {folder_to_share}
   browseable = yes
   read only = no
   guest ok = yes
""")

    run_command('sudo systemctl restart smbd')
    print_status(f"Carpeta {folder_to_share} compartida como {share_name}", 0)

def set_samba_permissions():
    folder_to_set = input("Ingrese la ruta completa de la carpeta para establecer permisos: ").strip()
    user = input("Ingrese el nombre de usuario que tendrá acceso: ").strip()

    if run_command(f'sudo chown -R {user}:{user} {folder_to_set}') and run_command(f'sudo chmod -R 0777 {folder_to_set}'):
        print_status(f"Permisos establecidos en {folder_to_set} para el usuario {user}", 0)
    else:
        print_status("Error al establecer permisos", 1)

def configure_nfs():
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("        Submenú de Configuración NFS")
        print("--------------------------------------------------")
        print("1. Instalar NFS Server")
        print("2. Compartir carpeta con NFS")
        print("3. Establecer permisos para NFS")
        print("4. Volver al menú principal")
        print("--------------------------------------------------")
        nfs_choice = input("Seleccione una opción [1-4]: ").strip()
        if nfs_choice == '1':
            install_nfs()
        elif nfs_choice == '2':
            share_folder_nfs()
        elif nfs_choice == '3':
            set_nfs_permissions()
        elif nfs_choice == '4':
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

def install_nfs():
    print("Instalando NFS Server...")
    if run_command('sudo apt-get update') and run_command('sudo apt-get install -y nfs-kernel-server'):
        print_status("NFS Server instalado", 0)
    else:
        print_status("Error al instalar NFS Server", 1)

def share_folder_nfs():
    folder_to_share = input("Ingrese la ruta completa de la carpeta a compartir: ").strip()
    client_ip = input("Ingrese la IP del cliente que tendrá acceso: ").strip()

    with open('/etc/exports', 'a') as exports:
        exports.write(f"{folder_to_share} {client_ip}(rw,sync,no_subtree_check)\n")

    run_command('sudo exportfs -a')
    run_command('sudo systemctl restart nfs-kernel-server')
    print_status(f"Carpeta {folder_to_share} compartida con el cliente {client_ip}", 0)

def set_nfs_permissions():
    folder_to_set = input("Ingrese la ruta completa de la carpeta para establecer permisos: ").strip()
    if run_command(f'sudo chmod -R 0777 {folder_to_set}'):
        print_status(f"Permisos 0777 establecidos en {folder_to_set}", 0)
    else:
        print_status("Error al establecer permisos", 1)

def main_menu():
    total_options = 35
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("           Menú de Instalación Mejorado")
        print("--------------------------------------------------")
        print("=== CONFIGURACIÓN BÁSICA ===")
        print("1. Configurar multipathd")
        print("2. Configurar zona horaria (America/Lima)")
        print("3. Crear usuarios SSH (con permisos sudo)")
        print("4. Configurar MySQL")
        print("5. Configurar MariaDB")
        print("6. Instalar Docker y Docker Compose (versión más reciente)")
        print("7. Instalar Nginx")
        print("8. Instalar PHP y módulos")
        print("9. Instalar Laravel")
        print("10. Instalar Git")
        print("11. Instalar Node.js, npm, PM2 y NVM")
        
        print("\n=== SEGURIDAD ===")
        print("12. Instalar Fail2Ban")
        print("13. Instalar y configurar UFW (Firewall)")
        print("14. Instalar Certbot para certificados SSL/TLS")
        print("15. Monitoreo SSH por log")
        
        print("\n=== SISTEMA Y OPTIMIZACIÓN ===")
        print("16. Expandir disco")
        print("17. Configurar memoria swap")
        print("18. Optimizar sistema")
        print("19. Automatizar optimización del sistema con cronjob")
        print("20. Configurar nuevo disco")
        
        print("\n=== DOCKER Y CONTENEDORES ===")
        print("21. Gestionar Contenedores Docker")
        print("22. Crear plantillas Docker Compose")
        
        print("\n=== RED ===")
        print("23. Configurar red")
        
        print("\n=== SERVICIOS DE ARCHIVOS ===")
        print("24. Configurar Samba")
        print("25. Configurar NFS")
        
        print("\n=== MONITOREO Y HERRAMIENTAS ===")
        print("26. Instalar herramientas de monitoreo")
        print("27. Instalar servicios comunes")
        print("28. Gestionar índices de Elasticsearch")
        
        print("\n=== MANTENIMIENTO ===")
        print("29. Crear backup del sistema")
        print("30. Actualizar script")
        
        print("\n=== SALIR ===")
        print("31. Salir")
        print("--------------------------------------------------")
        choice = input("Seleccione una opción [1-31]: ").strip()
        
        if choice == '1':
            configure_multipathd()
        elif choice == '2':
            configure_timezone()
        elif choice == '3':
            create_ssh_users()
        elif choice == '4':
            mysql_submenu()
        elif choice == '5':
            install_mariadb()
        elif choice == '6':
            install_docker()
        elif choice == '7':
            install_nginx()
        elif choice == '8':
            install_php()
        elif choice == '9':
            install_laravel()
        elif choice == '10':
            install_git()
        elif choice == '11':
            nodejs_submenu()
        elif choice == '12':
            install_fail2ban()
        elif choice == '13':
            install_ufw()
        elif choice == '14':
            install_certbot()
        elif choice == '15':
            configure_ssh_logging()
        elif choice == '16':
            expand_disk()
        elif choice == '17':
            configure_swap()
        elif choice == '18':
            optimize_system()
        elif choice == '19':
            configure_cronjob()
        elif choice == '20':
            configure_new_disk()
        elif choice == '21':
            docker_submenu()
        elif choice == '22':
            create_docker_compose_template()
        elif choice == '23':
            network_submenu()
        elif choice == '24':
            configure_samba()
        elif choice == '25':
            configure_nfs()
        elif choice == '26':
            install_monitoring_tools()
        elif choice == '27':
            install_common_services()
        elif choice == '28':
            manage_elasticsearch_indices()
        elif choice == '29':
            backup_system()
        elif choice == '30':
            update_script()
        elif choice == '31':
            print("Saliendo...")
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

if __name__ == "__main__":
    print("Buscando actualizaciones...")
    spinner = spinning_cursor()
    spinner_thread = threading.Thread(target=check_for_updates)
    spinner_thread.start()
    while spinner_thread.is_alive():
        print(next(spinner), end='\r')
        time.sleep(0.1)
    spinner_thread.join()
    print("Script ya actualizado.")
    
    if is_root():
        main_menu()
    else:
        print("Este script debe ejecutarse como root o utilizando sudo.")
