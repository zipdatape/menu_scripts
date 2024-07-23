import os
import getpass
import subprocess

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
    while True:
        choice = input("¿Quieres crear un usuario SSH adicional? (si/no): ").strip().lower()
        if choice in ['si', 's']:
            username = input("Ingrese el nombre del usuario: ").strip()
            password = getpass.getpass("Ingrese la contraseña para el usuario: ")
            if run_command(f'sudo adduser --gecos "" --disabled-password {username}') and run_command(f'echo "{username}:{password}" | sudo chpasswd'):
                print_status(f"Usuario SSH {username} creado", 0)
            else:
                print_status(f"Error al crear usuario SSH {username}", 1)
        elif choice in ['no', 'n']:
            break
        else:
            print("Por favor responda si o no.")

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
    choice = input("¿Quieres instalar Docker y Docker Compose? (si/no): ").strip().lower()
    if choice in ['si', 's']:
        if run_command('sudo apt-get update') and run_command('sudo apt-get install -y docker.io') and run_command('sudo systemctl start docker') and run_command('sudo systemctl enable docker') and run_command('sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose') and run_command('sudo chmod +x /usr/local/bin/docker-compose'):
            print_status("Docker y Docker Compose instalados", 0)
        else:
            print_status("Error al instalar Docker y Docker Compose", 1)

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


def main_menu():
    total_options = 17
    while True:
        os.system('clear')
        print("--------------------------------------------------")
        print("               Menú de Instalación")
        print("--------------------------------------------------")
        print("1. Configurar multipathd")
        print("2. Configurar zona horaria (America/Lima)")
        print("3. Crear usuarios SSH")
        print("4. Configurar MySQL")
        print("5. Configurar MariaDB")
        print("6. Instalar Docker y Docker Compose")
        print("7. Instalar Nginx")
        print("8. Instalar PHP y módulos")
        print("9. Instalar Laravel")
        print("10. Instalar Fail2Ban")
        print("11. Instalar y configurar UFW (Uncomplicated Firewall)")
        print("12. Instalar Git")
        print("13. Instalar Certbot para certificados SSL/TLS")
        print("14. Monitoreo SSH por log")
        print("15. Expandir disco")
        print("16. Automatizar optimización del sistema con cronjob")
        print("17. Gestionar Contenedores Docker")
        print("18. Salir")
        print("--------------------------------------------------")
        choice = input("Seleccione una opción [1-18]: ").strip()
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
            install_fail2ban()
        elif choice == '11':
            install_ufw()
        elif choice == '12':
            install_git()
        elif choice == '13':
            install_certbot()
        elif choice == '14':
            configure_ssh_logging()
        elif choice == '15':
            expand_disk()
        elif choice == '16':
            configure_cronjob()
        elif choice == '17':
            docker_submenu()
        elif choice == '18':
            print("Saliendo...")
            break
        else:
            print("Opción inválida! Por favor seleccione una opción válida.")
        input("Presione [Enter] para continuar...")

if __name__ == "__main__":
    if is_root():
        main_menu()
    else:
        print("Este script debe ejecutarse como root o utilizando sudo.")
