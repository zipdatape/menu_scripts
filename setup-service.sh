#!/bin/bash

# Script para configurar Setup Server Script como servicio
# Versión: 2.0.0

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Setup Server Script Service${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar si se ejecuta como root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Este script debe ejecutarse como root o con sudo"
        exit 1
    fi
}

# Obtener la ruta del script actual
get_script_path() {
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    SCRIPT_PATH="$SCRIPT_DIR/menu.py"
    
    if [[ ! -f "$SCRIPT_PATH" ]]; then
        print_error "No se encontró el archivo menu.py en $SCRIPT_DIR"
        exit 1
    fi
    
    print_status "Script encontrado en: $SCRIPT_PATH"
}

# Crear directorio de instalación
create_install_directory() {
    INSTALL_DIR="/opt/setup-server-script"
    
    if [[ ! -d "$INSTALL_DIR" ]]; then
        mkdir -p "$INSTALL_DIR"
        print_status "Directorio de instalación creado: $INSTALL_DIR"
    fi
    
    # Copiar archivos al directorio de instalación
    cp "$SCRIPT_PATH" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/" 2>/dev/null || true
    
    # Copiar directorio de ejemplos si existe
    if [[ -d "$SCRIPT_DIR/docker-compose-examples" ]]; then
        cp -r "$SCRIPT_DIR/docker-compose-examples" "$INSTALL_DIR/"
    fi
    
    # Establecer permisos
    chmod +x "$INSTALL_DIR/menu.py"
    chown -R root:root "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    print_status "Archivos copiados a $INSTALL_DIR"
}

# Crear script wrapper
create_wrapper_script() {
    WRAPPER_SCRIPT="/usr/local/bin/menu"
    
    cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash

# Wrapper script para Setup Server Script
# Permite ejecutar el script desde cualquier ubicación

SCRIPT_DIR="/opt/setup-server-script"
SCRIPT_PATH="$SCRIPT_DIR/menu.py"

# Verificar si el script existe
if [[ ! -f "$SCRIPT_PATH" ]]; then
    echo "Error: No se encontró el script menu.py en $SCRIPT_DIR"
    echo "Ejecute: sudo $0 --install"
    exit 1
fi

# Verificar dependencias de Python
check_python_deps() {
    python3 -c "import yaml, requests" 2>/dev/null
    if [[ $? -ne 0 ]]; then
        echo "Instalando dependencias de Python..."
        pip3 install PyYAML requests 2>/dev/null || {
            echo "Error: No se pudieron instalar las dependencias"
            echo "Ejecute manualmente: pip3 install PyYAML requests"
            exit 1
        }
    fi
}

# Función de ayuda
show_help() {
    echo "Setup Server Script - Menú de Administración del Servidor"
    echo ""
    echo "Uso: menu [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --help, -h     Mostrar esta ayuda"
    echo "  --version, -v  Mostrar versión"
    echo "  --install      Instalar/reinstalar el script"
    echo "  --uninstall    Desinstalar el script"
    echo "  --update       Actualizar el script"
    echo "  --status       Mostrar estado del servicio"
    echo ""
    echo "Sin opciones: Ejecutar el menú principal"
    echo ""
    echo "Ejemplos:"
    echo "  menu           # Ejecutar menú principal"
    echo "  menu --help    # Mostrar ayuda"
    echo "  menu --install # Instalar script"
}

# Función para mostrar versión
show_version() {
    echo "Setup Server Script v2.0.0"
    echo "Script de administración y configuración de servidores"
}

# Función para instalar
install_script() {
    echo "Instalando Setup Server Script..."
    
    # Verificar si se ejecuta como root
    if [[ $EUID -ne 0 ]]; then
        echo "Error: La instalación debe ejecutarse como root"
        echo "Ejecute: sudo $0 --install"
        exit 1
    fi
    
    # Ejecutar script de instalación si existe
    if [[ -f "$SCRIPT_DIR/install.sh" ]]; then
        bash "$SCRIPT_DIR/install.sh"
    else
        echo "Instalación manual..."
        check_python_deps
        
        # Crear directorio de backup
        mkdir -p /backup
        chmod 755 /backup
        
        # Configurar alias
        if [[ ! -f "/etc/profile.d/setup-server-aliases.sh" ]]; then
            cat > /etc/profile.d/setup-server-aliases.sh << 'ALIASEOF'
# Alias para Setup Server Script
alias menu='python3 /usr/local/bin/menu'
alias setup-server='python3 /usr/local/bin/menu'

# Alias útiles para administración del servidor
alias update-server='sudo apt-get update && sudo apt-get upgrade -y'
alias clean-server='sudo apt-get autoremove -y && sudo apt-get autoclean'
alias check-disk='df -h'
alias check-memory='free -h'
alias check-processes='htop'
alias check-services='systemctl list-units --type=service --state=running'
ALIASEOF
            chmod 644 /etc/profile.d/setup-server-aliases.sh
            echo "Alias configurados"
        fi
        
        echo "Instalación completada"
    fi
}

# Función para desinstalar
uninstall_script() {
    echo "Desinstalando Setup Server Script..."
    
    # Verificar si se ejecuta como root
    if [[ $EUID -ne 0 ]]; then
        echo "Error: La desinstalación debe ejecutarse como root"
        echo "Ejecute: sudo $0 --uninstall"
        exit 1
    fi
    
    # Eliminar archivos
    rm -rf /opt/setup-server-script
    rm -f /usr/local/bin/menu
    rm -f /etc/profile.d/setup-server-aliases.sh
    
    echo "Setup Server Script desinstalado"
}

# Función para actualizar
update_script() {
    echo "Actualizando Setup Server Script..."
    
    # Verificar si se ejecuta como root
    if [[ $EUID -ne 0 ]]; then
        echo "Error: La actualización debe ejecutarse como root"
        echo "Ejecute: sudo $0 --update"
        exit 1
    fi
    
    # Ejecutar actualización desde el script
    python3 "$SCRIPT_PATH" --update 2>/dev/null || {
        echo "Actualización manual..."
        # Aquí se podría agregar lógica para actualizar desde un repositorio
        echo "Función de actualización automática no disponible"
    }
}

# Función para mostrar estado
show_status() {
    echo "Estado de Setup Server Script:"
    echo ""
    
    if [[ -f "$SCRIPT_PATH" ]]; then
        echo "✓ Script principal: Instalado"
    else
        echo "✗ Script principal: No encontrado"
    fi
    
    if [[ -f "/usr/local/bin/menu" ]]; then
        echo "✓ Comando 'menu': Disponible"
    else
        echo "✗ Comando 'menu': No disponible"
    fi
    
    if [[ -f "/etc/profile.d/setup-server-aliases.sh" ]]; then
        echo "✓ Alias: Configurados"
    else
        echo "✗ Alias: No configurados"
    fi
    
    if [[ -d "/backup" ]]; then
        echo "✓ Directorio backup: Creado"
    else
        echo "✗ Directorio backup: No creado"
    fi
    
    # Verificar dependencias de Python
    python3 -c "import yaml, requests" 2>/dev/null
    if [[ $? -eq 0 ]]; then
        echo "✓ Dependencias Python: Instaladas"
    else
        echo "✗ Dependencias Python: Faltantes"
    fi
}

# Procesar argumentos
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --version|-v)
        show_version
        exit 0
        ;;
    --install)
        install_script
        exit 0
        ;;
    --uninstall)
        uninstall_script
        exit 0
        ;;
    --update)
        update_script
        exit 0
        ;;
    --status)
        show_status
        exit 0
        ;;
    "")
        # Sin argumentos: ejecutar el script principal
        check_python_deps
        python3 "$SCRIPT_PATH"
        ;;
    *)
        echo "Opción desconocida: $1"
        echo "Use --help para ver las opciones disponibles"
        exit 1
        ;;
esac
EOF

    chmod +x "$WRAPPER_SCRIPT"
    print_status "Script wrapper creado: $WRAPPER_SCRIPT"
}

# Crear servicio systemd
create_systemd_service() {
    SERVICE_FILE="/etc/systemd/system/setup-server-script.service"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Setup Server Script Service
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/true
ExecStop=/bin/true
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

    # Recargar systemd y habilitar servicio
    systemctl daemon-reload
    systemctl enable setup-server-script.service
    
    print_status "Servicio systemd creado y habilitado"
}

# Crear archivo de configuración global
create_global_config() {
    CONFIG_FILE="/etc/setup-server-script.conf"
    
    cat > "$CONFIG_FILE" << 'EOF'
# Configuración global para Setup Server Script
# Archivo: /etc/setup-server-script.conf

# Directorio de instalación
INSTALL_DIR="/opt/setup-server-script"

# Directorio de backup
BACKUP_DIR="/backup"

# Logs
LOG_FILE="/var/log/setup-server-script.log"

# Configuración de Docker
DOCKER_COMPOSE_VERSION="latest"
DOCKER_VERSION="latest"

# Configuración de seguridad
FAIL2BAN_ENABLED=true
UFW_ENABLED=true
SSH_KEY_AUTH_ONLY=false

# Configuración de optimización
SWAP_ENABLED=true
SWAP_SIZE_MB=2048
SYSTEM_OPTIMIZATION=true

# Configuración de monitoreo
MONITORING_TOOLS=true
COMMON_SERVICES=true
EOF

    chmod 644 "$CONFIG_FILE"
    print_status "Archivo de configuración global creado: $CONFIG_FILE"
}

# Crear archivo de log
setup_logging() {
    LOG_FILE="/var/log/setup-server-script.log"
    
    # Crear archivo de log si no existe
    touch "$LOG_FILE"
    chmod 644 "$LOG_FILE"
    
    print_status "Archivo de log configurado: $LOG_FILE"
}

# Crear alias globales
create_global_aliases() {
    ALIAS_FILE="/etc/profile.d/setup-server-aliases.sh"
    
    cat > "$ALIAS_FILE" << 'EOF'
# Alias para Setup Server Script
alias menu='python3 /usr/local/bin/menu'
alias setup-server='python3 /usr/local/bin/menu'
alias server-menu='python3 /usr/local/bin/menu'

# Alias útiles para administración del servidor
alias update-server='sudo apt-get update && sudo apt-get upgrade -y'
alias clean-server='sudo apt-get autoremove -y && sudo apt-get autoclean'
alias check-disk='df -h'
alias check-memory='free -h'
alias check-processes='htop'
alias check-services='systemctl list-units --type=service --state=running'
alias check-docker='docker ps -a'
alias check-ports='netstat -tulpn'
alias check-logs='journalctl -xe'
alias restart-services='sudo systemctl restart ssh nginx mysql docker'
alias backup-system='sudo menu --backup'
alias update-script='sudo menu --update'
EOF

    chmod 644 "$ALIAS_FILE"
    print_status "Alias globales configurados: $ALIAS_FILE"
}

# Crear script de desinstalación
create_uninstall_script() {
    UNINSTALL_SCRIPT="/usr/local/bin/uninstall-setup-server"
    
    cat > "$UNINSTALL_SCRIPT" << 'EOF'
#!/bin/bash

# Script de desinstalación para Setup Server Script

set -e

echo "Desinstalando Setup Server Script..."

# Verificar si se ejecuta como root
if [[ $EUID -ne 0 ]]; then
    echo "Error: Este script debe ejecutarse como root"
    echo "Ejecute: sudo $0"
    exit 1
fi

# Detener y deshabilitar servicio
systemctl stop setup-server-script.service 2>/dev/null || true
systemctl disable setup-server-script.service 2>/dev/null || true

# Eliminar archivos
rm -rf /opt/setup-server-script
rm -f /usr/local/bin/menu
rm -f /usr/local/bin/uninstall-setup-server
rm -f /etc/systemd/system/setup-server-script.service
rm -f /etc/profile.d/setup-server-aliases.sh
rm -f /etc/setup-server-script.conf

# Recargar systemd
systemctl daemon-reload

echo "Setup Server Script desinstalado completamente"
echo "Nota: Los directorios de backup (/backup) no se eliminan por seguridad"
EOF

    chmod +x "$UNINSTALL_SCRIPT"
    print_status "Script de desinstalación creado: $UNINSTALL_SCRIPT"
}

# Mostrar información de uso
show_usage_info() {
    echo
    print_status "Configuración del servicio completada exitosamente!"
    echo
    echo -e "${BLUE}Comandos disponibles:${NC}"
    echo "  menu                    # Ejecutar el script principal"
    echo "  menu --help             # Mostrar ayuda"
    echo "  menu --status           # Mostrar estado"
    echo "  menu --update           # Actualizar script"
    echo "  uninstall-setup-server  # Desinstalar completamente"
    echo
    echo -e "${BLUE}Alias útiles disponibles:${NC}"
    echo "  update-server           # Actualizar sistema"
    echo "  clean-server            # Limpiar paquetes"
    echo "  check-disk              # Verificar uso de disco"
    echo "  check-memory            # Verificar memoria"
    echo "  check-processes         # Ver procesos (htop)"
    echo "  check-services          # Ver servicios activos"
    echo "  check-docker            # Ver contenedores Docker"
    echo "  check-ports             # Ver puertos abiertos"
    echo "  check-logs              # Ver logs del sistema"
    echo "  restart-services        # Reiniciar servicios críticos"
    echo
    echo -e "${BLUE}Para aplicar los alias, ejecuta:${NC}"
    echo "  source /etc/profile.d/setup-server-aliases.sh"
    echo "  # O reinicia la sesión"
    echo
    echo -e "${BLUE}Archivos importantes:${NC}"
    echo "  Script principal: /opt/setup-server-script/menu.py"
    echo "  Comando: /usr/local/bin/menu"
    echo "  Configuración: /etc/setup-server-script.conf"
    echo "  Logs: /var/log/setup-server-script.log"
    echo "  Backup: /backup"
    echo
    print_warning "IMPORTANTE: Para usar todas las funcionalidades, ejecuta:"
    echo "  sudo menu"
    echo
}

# Función principal
main() {
    print_header
    
    # Verificaciones iniciales
    check_root
    get_script_path
    
    # Instalación
    create_install_directory
    create_wrapper_script
    create_systemd_service
    create_global_config
    setup_logging
    create_global_aliases
    create_uninstall_script
    
    # Información final
    show_usage_info
}

# Ejecutar función principal
main "$@" 