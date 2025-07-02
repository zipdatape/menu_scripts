#!/bin/bash

# Script de diagnóstico para Docker
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
    echo -e "${BLUE}  Diagnóstico de Docker${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Función para verificar comando
check_command() {
    local cmd="$1"
    local description="$2"
    
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "✓ $description"
        return 0
    else
        echo -e "✗ $description"
        return 1
    fi
}

# Función para verificar servicio
check_service() {
    local service="$1"
    local description="$2"
    
    if systemctl is-active "$service" >/dev/null 2>&1; then
        echo -e "✓ $description (activo)"
        return 0
    elif systemctl is-enabled "$service" >/dev/null 2>&1; then
        echo -e "⚠ $description (habilitado pero inactivo)"
        return 1
    else
        echo -e "✗ $description (no encontrado)"
        return 1
    fi
}

# Función para verificar archivo
check_file() {
    local file="$1"
    local description="$2"
    
    if [[ -f "$file" ]]; then
        echo -e "✓ $description"
        return 0
    else
        echo -e "✗ $description"
        return 1
    fi
}

# Función para verificar directorio
check_directory() {
    local dir="$1"
    local description="$2"
    
    if [[ -d "$dir" ]]; then
        echo -e "✓ $description"
        return 0
    else
        echo -e "✗ $description"
        return 1
    fi
}

# Función para mostrar información del sistema
show_system_info() {
    echo -e "${BLUE}Información del Sistema:${NC}"
    echo "Sistema operativo: $(lsb_release -d | cut -f2)"
    echo "Kernel: $(uname -r)"
    echo "Arquitectura: $(uname -m)"
    echo "Usuario actual: $(whoami)"
    echo "Grupos del usuario: $(groups)"
    echo ""
}

# Función para verificar dependencias
check_dependencies() {
    echo -e "${BLUE}Verificando Dependencias:${NC}"
    
    local deps=("curl" "wget" "gnupg" "lsb-release" "apt-transport-https" "ca-certificates")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if dpkg -l | grep -q "^ii.*$dep"; then
            echo -e "✓ $dep instalado"
        else
            echo -e "✗ $dep faltante"
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo ""
        print_warning "Dependencias faltantes: ${missing_deps[*]}"
        echo "Para instalar: sudo apt-get install -y ${missing_deps[*]}"
    fi
    echo ""
}

# Función para verificar repositorios Docker
check_docker_repos() {
    echo -e "${BLUE}Verificando Repositorios Docker:${NC}"
    
    # Verificar archivo de clave
    if check_file "/usr/share/keyrings/docker-archive-keyring.gpg" "Clave GPG de Docker"; then
        echo "  Tamaño: $(stat -c %s /usr/share/keyrings/docker-archive-keyring.gpg) bytes"
    fi
    
    # Verificar archivo de repositorio
    if check_file "/etc/apt/sources.list.d/docker.list" "Archivo de repositorio Docker"; then
        echo "  Contenido:"
        cat /etc/apt/sources.list.d/docker.list | sed 's/^/    /'
    fi
    
    # Verificar si el repositorio está disponible
    if apt-cache policy docker-ce >/dev/null 2>&1; then
        echo -e "✓ Repositorio Docker disponible"
        echo "  Versiones disponibles:"
        apt-cache policy docker-ce | grep -E "Installed|Candidate" | sed 's/^/    /'
    else
        echo -e "✗ Repositorio Docker no disponible"
    fi
    echo ""
}

# Función para verificar instalación de Docker
check_docker_installation() {
    echo -e "${BLUE}Verificando Instalación de Docker:${NC}"
    
    # Verificar comandos
    check_command "docker" "Comando docker"
    check_command "docker-compose" "Comando docker-compose"
    check_command "docker-buildx" "Comando docker-buildx"
    
    # Verificar versiones
    if command -v docker >/dev/null 2>&1; then
        echo "  Versión Docker: $(docker --version)"
    fi
    
    if command -v docker-compose >/dev/null 2>&1; then
        echo "  Versión Docker Compose: $(docker-compose --version)"
    fi
    
    echo ""
}

# Función para verificar servicio Docker
check_docker_service() {
    echo -e "${BLUE}Verificando Servicio Docker:${NC}"
    
    check_service "docker" "Servicio Docker"
    check_service "containerd" "Servicio Containerd"
    
    # Verificar estado detallado
    if systemctl is-active docker >/dev/null 2>&1; then
        echo "  Estado detallado:"
        systemctl status docker --no-pager -l | head -10 | sed 's/^/    /'
    fi
    
    echo ""
}

# Función para verificar permisos y grupos
check_permissions() {
    echo -e "${BLUE}Verificando Permisos y Grupos:${NC}"
    
    current_user=$(whoami)
    echo "Usuario actual: $current_user"
    
    # Verificar grupo docker
    if groups | grep -q docker; then
        echo -e "✓ Usuario en grupo docker"
    else
        echo -e "✗ Usuario NO está en grupo docker"
        echo "  Para agregar: sudo usermod -aG docker $current_user"
    fi
    
    # Verificar socket Docker
    if [[ -S /var/run/docker.sock ]]; then
        echo -e "✓ Socket Docker existe"
        echo "  Permisos: $(stat -c %a /var/run/docker.sock)"
        echo "  Propietario: $(stat -c %U:%G /var/run/docker.sock)"
    else
        echo -e "✗ Socket Docker no existe"
    fi
    
    echo ""
}

# Función para probar Docker
test_docker() {
    echo -e "${BLUE}Probando Docker:${NC}"
    
    # Probar comando docker info
    if sudo docker info >/dev/null 2>&1; then
        echo -e "✓ Docker info funciona"
    else
        echo -e "✗ Docker info falla"
        echo "  Error: $(sudo docker info 2>&1 | head -5)"
    fi
    
    # Probar comando docker run
    if sudo docker run --rm hello-world >/dev/null 2>&1; then
        echo -e "✓ Docker run funciona"
    else
        echo -e "✗ Docker run falla"
        echo "  Error: $(sudo docker run --rm hello-world 2>&1 | head -5)"
    fi
    
    # Probar Docker Compose
    if command -v docker-compose >/dev/null 2>&1; then
        if docker-compose --version >/dev/null 2>&1; then
            echo -e "✓ Docker Compose funciona"
        else
            echo -e "✗ Docker Compose falla"
        fi
    fi
    
    echo ""
}

# Función para verificar configuración de red
check_network() {
    echo -e "${BLUE}Verificando Configuración de Red:${NC}"
    
    # Verificar interfaces de red
    echo "Interfaces de red:"
    ip link show | grep -E "^[0-9]+:" | sed 's/^/  /'
    
    # Verificar bridge Docker
    if ip link show docker0 >/dev/null 2>&1; then
        echo -e "✓ Bridge Docker (docker0) existe"
        echo "  Estado: $(ip link show docker0 | grep -o 'state [A-Z]*')"
    else
        echo -e "✗ Bridge Docker (docker0) no existe"
    fi
    
    # Verificar iptables
    if sudo iptables -L >/dev/null 2>&1; then
        echo -e "✓ iptables funciona"
        echo "  Reglas Docker:"
        sudo iptables -L | grep -i docker | head -5 | sed 's/^/    /'
    else
        echo -e "✗ iptables no funciona"
    fi
    
    echo ""
}

# Función para verificar logs
check_logs() {
    echo -e "${BLUE}Verificando Logs:${NC}"
    
    # Verificar logs de Docker
    if journalctl -u docker --no-pager -n 10 >/dev/null 2>&1; then
        echo "Últimos logs de Docker:"
        journalctl -u docker --no-pager -n 5 | sed 's/^/  /'
    else
        echo -e "✗ No se pueden leer logs de Docker"
    fi
    
    # Verificar logs del sistema
    echo "Últimos logs del sistema relacionados con Docker:"
    journalctl --no-pager -n 10 | grep -i docker | head -5 | sed 's/^/  /'
    
    echo ""
}

# Función para mostrar recomendaciones
show_recommendations() {
    echo -e "${BLUE}Recomendaciones:${NC}"
    
    # Verificar si Docker está instalado
    if ! command -v docker >/dev/null 2>&1; then
        echo "1. Docker no está instalado. Instalar usando:"
        echo "   sudo apt-get update"
        echo "   sudo apt-get install -y docker.io docker-compose"
        echo "   sudo systemctl start docker"
        echo "   sudo systemctl enable docker"
        echo "   sudo usermod -aG docker $USER"
    fi
    
    # Verificar si el usuario está en el grupo docker
    if ! groups | grep -q docker; then
        echo "2. Agregar usuario al grupo docker:"
        echo "   sudo usermod -aG docker $USER"
        echo "   # Luego cerrar sesión y volver a iniciar"
    fi
    
    # Verificar si el servicio está activo
    if ! systemctl is-active docker >/dev/null 2>&1; then
        echo "3. Iniciar servicio Docker:"
        echo "   sudo systemctl start docker"
        echo "   sudo systemctl enable docker"
    fi
    
    # Verificar repositorio
    if ! apt-cache policy docker-ce >/dev/null 2>&1; then
        echo "4. Configurar repositorio oficial de Docker:"
        echo "   curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
        echo "   echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null"
        echo "   sudo apt-get update"
        echo "   sudo apt-get install -y docker-ce docker-ce-cli containerd.io"
    fi
    
    echo ""
}

# Función para reparación automática
auto_fix() {
    echo -e "${BLUE}Intentando Reparación Automática:${NC}"
    
    # Verificar si se ejecuta como root
    if [[ $EUID -ne 0 ]]; then
        print_error "La reparación automática requiere permisos de root"
        echo "Ejecute: sudo $0 --fix"
        return 1
    fi
    
    # Reparar dependencias
    print_status "Reparando dependencias..."
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Reparar repositorio Docker
    print_status "Reparando repositorio Docker..."
    rm -f /usr/share/keyrings/docker-archive-keyring.gpg
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    
    # Reparar instalación de Docker
    print_status "Reparando instalación de Docker..."
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Reparar servicio
    print_status "Reparando servicio Docker..."
    systemctl start docker
    systemctl enable docker
    
    # Reparar permisos
    current_user=${SUDO_USER:-$USER}
    if [[ "$current_user" != "root" ]]; then
        print_status "Reparando permisos de usuario..."
        usermod -aG docker "$current_user"
    fi
    
    print_status "Reparación completada"
    echo "Recomendación: Cerrar sesión y volver a iniciar para aplicar cambios de grupo"
}

# Función de ayuda
show_help() {
    echo "Script de Diagnóstico para Docker"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --fix, -f       Intentar reparación automática (requiere root)"
    echo "  --help, -h      Mostrar esta ayuda"
    echo ""
    echo "Sin opciones: Diagnóstico completo"
    echo ""
    echo "Ejemplos:"
    echo "  $0              # Diagnóstico completo"
    echo "  sudo $0 --fix   # Reparación automática"
    echo "  $0 --help       # Mostrar ayuda"
}

# Función principal de diagnóstico
main_diagnostic() {
    print_header
    
    show_system_info
    check_dependencies
    check_docker_repos
    check_docker_installation
    check_docker_service
    check_permissions
    test_docker
    check_network
    check_logs
    show_recommendations
    
    echo -e "${BLUE}Diagnóstico completado${NC}"
}

# Procesar argumentos
case "${1:-}" in
    --fix|-f)
        auto_fix
        ;;
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        main_diagnostic
        ;;
    *)
        echo "Opción desconocida: $1"
        echo "Use --help para ver las opciones disponibles"
        exit 1
        ;;
esac 