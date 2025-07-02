#!/bin/bash

# Script de instalación mejorado para Docker
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
    echo -e "${BLUE}  Instalador de Docker Mejorado${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Función para ejecutar comandos con manejo de errores
run_command() {
    local cmd="$1"
    local description="$2"
    
    echo -n "Ejecutando: $description... "
    
    if eval "$cmd" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Función para verificar si Docker ya está instalado
check_docker_installed() {
    if command -v docker >/dev/null 2>&1; then
        local version=$(docker --version)
        print_warning "Docker ya está instalado: $version"
        
        read -p "¿Deseas reinstalar Docker? (si/no): " choice
        case "$choice" in
            [Ss][Ii]|[Ss])
                print_status "Procediendo con reinstalación..."
                return 0
                ;;
            *)
                print_status "Instalación cancelada."
                exit 0
                ;;
        esac
    fi
    return 0
}

# Función para verificar sistema operativo
check_os() {
    print_status "Verificando sistema operativo..."
    
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    else
        print_error "No se pudo detectar el sistema operativo"
        exit 1
    fi
    
    print_status "Sistema detectado: $OS $VER"
    
    # Verificar si es Ubuntu/Debian
    if [[ "$OS" != *"Ubuntu"* ]] && [[ "$OS" != *"Debian"* ]]; then
        print_warning "Este script está optimizado para Ubuntu/Debian"
        print_warning "Otros sistemas pueden requerir ajustes manuales"
    fi
}

# Función para instalar dependencias
install_dependencies() {
    print_status "Instalando dependencias..."
    
    local deps=(
        "apt-transport-https"
        "ca-certificates"
        "curl"
        "gnupg"
        "lsb-release"
        "software-properties-common"
    )
    
    for dep in "${deps[@]}"; do
        if ! run_command "sudo apt-get install -y $dep" "Instalando $dep"; then
            print_error "Error al instalar $dep"
            return 1
        fi
    done
    
    return 0
}

# Función para configurar repositorio Docker
setup_docker_repo() {
    print_status "Configurando repositorio Docker..."
    
    # Limpiar configuración anterior si existe
    if [[ -f /usr/share/keyrings/docker-archive-keyring.gpg ]]; then
        print_status "Eliminando configuración anterior..."
        sudo rm -f /usr/share/keyrings/docker-archive-keyring.gpg
    fi
    
    if [[ -f /etc/apt/sources.list.d/docker.list ]]; then
        sudo rm -f /etc/apt/sources.list.d/docker.list
    fi
    
    # Agregar clave GPG
    if ! run_command "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg" "Agregando clave GPG"; then
        print_error "Error al agregar clave GPG"
        return 1
    fi
    
    # Agregar repositorio
    local repo_cmd="echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null"
    
    if ! run_command "$repo_cmd" "Agregando repositorio Docker"; then
        print_error "Error al agregar repositorio"
        return 1
    fi
    
    # Actualizar repositorios
    if ! run_command "sudo apt-get update" "Actualizando repositorios"; then
        print_error "Error al actualizar repositorios"
        return 1
    fi
    
    return 0
}

# Función para instalar Docker
install_docker_packages() {
    print_status "Instalando Docker..."
    
    local packages=(
        "docker-ce"
        "docker-ce-cli"
        "containerd.io"
        "docker-buildx-plugin"
        "docker-compose-plugin"
    )
    
    for pkg in "${packages[@]}"; do
        if ! run_command "sudo apt-get install -y $pkg" "Instalando $pkg"; then
            print_error "Error al instalar $pkg"
            return 1
        fi
    done
    
    return 0
}

# Función para instalar Docker Compose standalone
install_docker_compose_standalone() {
    print_status "Instalando Docker Compose standalone..."
    
    # Obtener versión más reciente
    local compose_version=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    
    if [[ -z "$compose_version" ]]; then
        compose_version="v2.20.0"  # Versión por defecto
    fi
    
    print_status "Instalando Docker Compose $compose_version"
    
    local compose_url="https://github.com/docker/compose/releases/download/${compose_version}/docker-compose-$(uname -s)-$(uname -m)"
    
    if ! run_command "sudo curl -L \"$compose_url\" -o /usr/local/bin/docker-compose" "Descargando Docker Compose"; then
        print_error "Error al descargar Docker Compose"
        return 1
    fi
    
    if ! run_command "sudo chmod +x /usr/local/bin/docker-compose" "Configurando permisos"; then
        print_error "Error al configurar permisos"
        return 1
    fi
    
    return 0
}

# Función para configurar Docker
configure_docker() {
    print_status "Configurando Docker..."
    
    # Iniciar servicio
    if ! run_command "sudo systemctl start docker" "Iniciando servicio Docker"; then
        print_error "Error al iniciar servicio Docker"
        return 1
    fi
    
    # Habilitar servicio
    if ! run_command "sudo systemctl enable docker" "Habilitando servicio Docker"; then
        print_error "Error al habilitar servicio Docker"
        return 1
    fi
    
    # Agregar usuario al grupo docker
    local current_user=${SUDO_USER:-$USER}
    if [[ "$current_user" != "root" ]]; then
        if ! run_command "sudo usermod -aG docker $current_user" "Agregando usuario al grupo docker"; then
            print_warning "No se pudo agregar usuario al grupo docker"
            print_warning "Ejecuta manualmente: sudo usermod -aG docker $current_user"
        fi
    fi
    
    return 0
}

# Función para verificar instalación
verify_installation() {
    print_status "Verificando instalación..."
    
    # Verificar Docker
    if command -v docker >/dev/null 2>&1; then
        local docker_version=$(docker --version)
        print_status "Docker instalado: $docker_version"
    else
        print_error "Docker no está instalado correctamente"
        return 1
    fi
    
    # Verificar Docker Compose
    if command -v docker-compose >/dev/null 2>&1; then
        local compose_version=$(docker-compose --version)
        print_status "Docker Compose instalado: $compose_version"
    else
        print_error "Docker Compose no está instalado correctamente"
        return 1
    fi
    
    # Probar Docker
    if sudo docker info >/dev/null 2>&1; then
        print_status "Docker funcionando correctamente"
    else
        print_error "Docker no está funcionando correctamente"
        return 1
    fi
    
    # Probar Docker Compose
    if docker-compose --version >/dev/null 2>&1; then
        print_status "Docker Compose funcionando correctamente"
    else
        print_error "Docker Compose no está funcionando correctamente"
        return 1
    fi
    
    return 0
}

# Función para mostrar información post-instalación
show_post_install_info() {
    echo ""
    print_status "Instalación completada exitosamente!"
    echo ""
    echo -e "${BLUE}Información importante:${NC}"
    echo "1. Para usar Docker sin sudo, cierra sesión y vuelve a iniciar"
    echo "2. O ejecuta: newgrp docker"
    echo ""
    echo -e "${BLUE}Comandos útiles:${NC}"
    echo "• Verificar instalación: docker --version && docker-compose --version"
    echo "• Probar Docker: sudo docker run hello-world"
    echo "• Ver información del sistema: sudo docker info"
    echo "• Ver contenedores: sudo docker ps -a"
    echo ""
    echo -e "${BLUE}Documentación:${NC}"
    echo "• Docker: https://docs.docker.com/"
    echo "• Docker Compose: https://docs.docker.com/compose/"
    echo ""
}

# Función para diagnóstico rápido
quick_diagnostic() {
    echo ""
    print_status "Ejecutando diagnóstico rápido..."
    
    # Verificar comandos
    if command -v docker >/dev/null 2>&1; then
        echo "✓ Docker: $(docker --version)"
    else
        echo "✗ Docker: No instalado"
    fi
    
    if command -v docker-compose >/dev/null 2>&1; then
        echo "✓ Docker Compose: $(docker-compose --version)"
    else
        echo "✗ Docker Compose: No instalado"
    fi
    
    # Verificar servicio
    if systemctl is-active docker >/dev/null 2>&1; then
        echo "✓ Servicio Docker: Activo"
    else
        echo "✗ Servicio Docker: Inactivo"
    fi
    
    # Verificar grupo
    if groups | grep -q docker; then
        echo "✓ Usuario en grupo docker"
    else
        echo "✗ Usuario NO está en grupo docker"
    fi
    
    echo ""
}

# Función principal
main() {
    print_header
    
    # Verificar permisos de root
    if [[ $EUID -eq 0 ]]; then
        print_error "No ejecutes este script como root"
        print_error "Ejecuta: sudo $0"
        exit 1
    fi
    
    # Verificar si sudo está disponible
    if ! command -v sudo >/dev/null 2>&1; then
        print_error "sudo no está disponible"
        exit 1
    fi
    
    # Verificar sistema operativo
    check_os
    
    # Verificar si Docker ya está instalado
    check_docker_installed
    
    # Instalar dependencias
    if ! install_dependencies; then
        print_error "Error al instalar dependencias"
        exit 1
    fi
    
    # Configurar repositorio
    if ! setup_docker_repo; then
        print_error "Error al configurar repositorio"
        exit 1
    fi
    
    # Instalar Docker
    if ! install_docker_packages; then
        print_error "Error al instalar Docker"
        exit 1
    fi
    
    # Instalar Docker Compose standalone
    if ! install_docker_compose_standalone; then
        print_warning "Error al instalar Docker Compose standalone"
        print_warning "Se usará la versión del plugin si está disponible"
    fi
    
    # Configurar Docker
    if ! configure_docker; then
        print_error "Error al configurar Docker"
        exit 1
    fi
    
    # Verificar instalación
    if ! verify_installation; then
        print_error "Error en la verificación de instalación"
        exit 1
    fi
    
    # Mostrar información post-instalación
    show_post_install_info
    
    # Diagnóstico rápido
    quick_diagnostic
    
    print_status "¡Instalación completada!"
}

# Función de ayuda
show_help() {
    echo "Instalador de Docker Mejorado"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --help, -h      Mostrar esta ayuda"
    echo "  --diagnostic    Solo ejecutar diagnóstico"
    echo ""
    echo "Sin opciones: Instalación completa"
    echo ""
    echo "Ejemplos:"
    echo "  $0              # Instalación completa"
    echo "  $0 --diagnostic # Solo diagnóstico"
    echo "  $0 --help       # Mostrar ayuda"
}

# Procesar argumentos
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --diagnostic)
        quick_diagnostic
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "Opción desconocida: $1"
        echo "Use --help para ver las opciones disponibles"
        exit 1
        ;;
esac 