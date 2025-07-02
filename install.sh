#!/bin/bash

# Script de instalación automática para Setup Server Script
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
    echo -e "${BLUE}  Setup Server Script Installer${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar si se ejecuta como root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Este script debe ejecutarse como root o con sudo"
        exit 1
    fi
}

# Verificar sistema operativo
check_os() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "No se pudo detectar el sistema operativo"
        exit 1
    fi
    
    source /etc/os-release
    
    if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
        print_warning "Este script está diseñado para Ubuntu/Debian. Otros sistemas pueden no funcionar correctamente."
        read -p "¿Continuar de todas formas? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_status "Sistema operativo detectado: $PRETTY_NAME"
}

# Actualizar sistema
update_system() {
    print_status "Actualizando sistema..."
    apt-get update
    apt-get upgrade -y
    print_status "Sistema actualizado"
}

# Instalar dependencias del sistema
install_system_dependencies() {
    print_status "Instalando dependencias del sistema..."
    
    # Dependencias básicas
    apt-get install -y python3 python3-pip python3-venv curl wget git
    
    # Dependencias para Docker
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Dependencias para herramientas de monitoreo
    apt-get install -y htop vim nano tree net-tools
    
    print_status "Dependencias del sistema instaladas"
}

# Instalar dependencias de Python
install_python_dependencies() {
    print_status "Instalando dependencias de Python..."
    
    # Actualizar pip
    python3 -m pip install --upgrade pip
    
    # Instalar dependencias desde requirements.txt
    if [[ -f "requirements.txt" ]]; then
        pip3 install -r requirements.txt
    else
        # Instalar dependencias manualmente si no existe requirements.txt
        pip3 install PyYAML requests
    fi
    
    print_status "Dependencias de Python instaladas"
}

# Configurar permisos del script
setup_permissions() {
    print_status "Configurando permisos..."
    
    # Hacer el script ejecutable
    chmod +x menu.py
    
    # Crear enlace simbólico para acceso global
    if [[ ! -f "/usr/local/bin/setup-server" ]]; then
        ln -sf "$(pwd)/menu.py" /usr/local/bin/setup-server
        print_status "Enlace simbólico creado: setup-server"
    fi
    
    print_status "Permisos configurados"
}

# Crear directorio de backup
setup_backup_directory() {
    print_status "Configurando directorio de backup..."
    
    mkdir -p /backup
    chmod 755 /backup
    
    print_status "Directorio de backup configurado en /backup"
}

# Configurar alias útiles
setup_aliases() {
    print_status "Configurando alias útiles..."
    
    # Crear archivo de alias si no existe
    if [[ ! -f "/etc/profile.d/setup-server-aliases.sh" ]]; then
        cat > /etc/profile.d/setup-server-aliases.sh << 'EOF'
# Alias para Setup Server Script
alias setup-server='python3 /usr/local/bin/setup-server'
alias server-menu='python3 /usr/local/bin/setup-server'

# Alias útiles para administración del servidor
alias update-server='sudo apt-get update && sudo apt-get upgrade -y'
alias clean-server='sudo apt-get autoremove -y && sudo apt-get autoclean'
alias check-disk='df -h'
alias check-memory='free -h'
alias check-processes='htop'
alias check-services='systemctl list-units --type=service --state=running'
EOF
        chmod 644 /etc/profile.d/setup-server-aliases.sh
        print_status "Alias configurados"
    fi
}

# Mostrar información de uso
show_usage_info() {
    echo
    print_status "Instalación completada exitosamente!"
    echo
    echo -e "${BLUE}Uso del script:${NC}"
    echo "  setup-server          # Ejecutar el script principal"
    echo "  server-menu           # Alias alternativo"
    echo
    echo -e "${BLUE}Alias útiles disponibles:${NC}"
    echo "  update-server         # Actualizar sistema"
    echo "  clean-server          # Limpiar paquetes"
    echo "  check-disk            # Verificar uso de disco"
    echo "  check-memory          # Verificar memoria"
    echo "  check-processes       # Ver procesos (htop)"
    echo "  check-services        # Ver servicios activos"
    echo
    echo -e "${BLUE}Para aplicar los alias, ejecuta:${NC}"
    echo "  source /etc/profile.d/setup-server-aliases.sh"
    echo "  # O reinicia la sesión"
    echo
    print_warning "IMPORTANTE: Para usar todas las funcionalidades, ejecuta el script como root:"
    echo "  sudo setup-server"
    echo
}

# Función principal
main() {
    print_header
    
    # Verificaciones iniciales
    check_root
    check_os
    
    # Instalación
    update_system
    install_system_dependencies
    install_python_dependencies
    setup_permissions
    setup_backup_directory
    setup_aliases
    
    # Información final
    show_usage_info
}

# Ejecutar función principal
main "$@" 