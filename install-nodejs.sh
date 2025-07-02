#!/bin/bash

# Script de instalación completa para Node.js, npm, PM2 y NVM
# Versión: 1.0.0

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
    echo -e "${BLUE}  Instalador de Node.js Completo${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Función para ejecutar comandos con manejo de errores
run_command() {
    local cmd="$1"
    local description="$2"
    
    if [[ -n "$description" ]]; then
        echo -n "Ejecutando: $description... "
    fi
    
    if eval "$cmd" >/dev/null 2>&1; then
        if [[ -n "$description" ]]; then
            echo -e "${GREEN}✓${NC}"
        fi
        return 0
    else
        if [[ -n "$description" ]]; then
            echo -e "${RED}✗${NC}"
        fi
        return 1
    fi
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
        "curl"
        "wget"
        "gnupg"
        "software-properties-common"
        "build-essential"
    )
    
    if ! run_command "sudo apt-get update" "Actualizando repositorios"; then
        print_error "Error al actualizar repositorios"
        return 1
    fi
    
    for dep in "${deps[@]}"; do
        if ! run_command "sudo apt-get install -y $dep" "Instalando $dep"; then
            print_error "Error al instalar $dep"
            return 1
        fi
    done
    
    return 0
}

# Función para instalar Node.js desde NodeSource
install_nodejs_nodesource() {
    print_status "Instalando Node.js desde NodeSource (método recomendado)..."
    
    # Obtener script de instalación de NodeSource
    if ! run_command "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -" "Configurando repositorio NodeSource"; then
        return 1
    fi
    
    # Instalar Node.js
    if ! run_command "sudo apt-get install -y nodejs" "Instalando Node.js"; then
        return 1
    fi
    
    # Verificar instalación
    if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
        local node_version=$(node --version)
        local npm_version=$(npm --version)
        print_status "Node.js instalado: $node_version"
        print_status "npm instalado: $npm_version"
        return 0
    else
        return 1
    fi
}

# Función para instalar Node.js con Snap
install_nodejs_snap() {
    print_status "Instalando Node.js con Snap..."
    
    # Verificar si snap está disponible
    if ! command -v snap >/dev/null 2>&1; then
        if ! run_command "sudo apt-get install -y snapd" "Instalando snapd"; then
            return 1
        fi
    fi
    
    # Instalar Node.js con snap
    if ! run_command "sudo snap install node --classic" "Instalando Node.js con snap"; then
        return 1
    fi
    
    # Verificar instalación
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        print_status "Node.js instalado con snap: $node_version"
        return 0
    else
        return 1
    fi
}

# Función para instalar Node.js desde repositorios de Ubuntu
install_nodejs_ubuntu() {
    print_status "Instalando Node.js desde repositorios de Ubuntu..."
    
    if ! run_command "sudo apt-get update" "Actualizando repositorios"; then
        return 1
    fi
    
    if ! run_command "sudo apt-get install -y nodejs npm" "Instalando Node.js y npm"; then
        return 1
    fi
    
    # Verificar instalación
    if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
        local node_version=$(node --version)
        local npm_version=$(npm --version)
        print_status "Node.js instalado: $node_version"
        print_status "npm instalado: $npm_version"
        return 0
    else
        return 1
    fi
}

# Función para instalar NVM
install_nvm() {
    print_status "Instalando NVM (Node Version Manager)..."
    
    # Obtener la versión más reciente de NVM
    local nvm_version
    nvm_version=$(curl -s https://api.github.com/repos/nvm-sh/nvm/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    
    if [[ -z "$nvm_version" ]]; then
        nvm_version="v0.39.0"  # Versión por defecto
    fi
    
    print_status "Instalando NVM $nvm_version..."
    
    # Instalar NVM
    local install_cmd="curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/${nvm_version}/install.sh | bash"
    
    if ! run_command "$install_cmd" "Descargando e instalando NVM"; then
        return 1
    fi
    
    # Configurar variables de entorno
    local nvm_config='
# NVM Configuration
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
'
    
    # Agregar configuración a .bashrc si no existe
    local bashrc_path="$HOME/.bashrc"
    if [[ -f "$bashrc_path" ]]; then
        if ! grep -q "NVM_DIR" "$bashrc_path"; then
            echo "$nvm_config" >> "$bashrc_path"
            print_status "Configuración de NVM agregada a .bashrc"
        fi
    fi
    
    # Agregar configuración a .zshrc si existe
    local zshrc_path="$HOME/.zshrc"
    if [[ -f "$zshrc_path" ]]; then
        if ! grep -q "NVM_DIR" "$zshrc_path"; then
            echo "$nvm_config" >> "$zshrc_path"
            print_status "Configuración de NVM agregada a .zshrc"
        fi
    fi
    
    print_status "NVM instalado correctamente"
    print_status "Para usar NVM, ejecuta: source ~/.bashrc"
    
    return 0
}

# Función para instalar PM2
install_pm2() {
    print_status "Instalando PM2 (Process Manager 2)..."
    
    # Verificar si npm está disponible
    if ! command -v npm >/dev/null 2>&1; then
        print_error "npm no está instalado. Instala Node.js primero."
        return 1
    fi
    
    # Instalar PM2 globalmente
    if ! run_command "sudo npm install -g pm2" "Instalando PM2 globalmente"; then
        return 1
    fi
    
    # Verificar instalación
    if command -v pm2 >/dev/null 2>&1; then
        local pm2_version=$(pm2 --version)
        print_status "PM2 instalado: versión $pm2_version"
        
        # Configurar PM2 para inicio automático
        print_status "Configurando PM2 para inicio automático..."
        local startup_cmd=$(pm2 startup 2>/dev/null | grep "sudo")
        if [[ -n "$startup_cmd" ]]; then
            echo "Para completar la configuración de PM2, ejecuta:"
            echo "$startup_cmd"
        fi
        
        return 0
    else
        return 1
    fi
}

# Función para verificar todas las instalaciones
verify_installations() {
    print_status "Verificando instalaciones..."
    echo "=" * 50
    
    # Verificar Node.js
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        echo "✓ Node.js: $node_version"
    else
        echo "✗ Node.js: No instalado"
    fi
    
    # Verificar npm
    if command -v npm >/dev/null 2>&1; then
        local npm_version=$(npm --version)
        echo "✓ npm: $npm_version"
    else
        echo "✗ npm: No instalado"
    fi
    
    # Verificar PM2
    if command -v pm2 >/dev/null 2>&1; then
        local pm2_version=$(pm2 --version)
        echo "✓ PM2: $pm2_version"
    else
        echo "✗ PM2: No instalado"
    fi
    
    # Verificar NVM
    local nvm_dir="$HOME/.nvm"
    if [[ -d "$nvm_dir" ]]; then
        echo "✓ NVM: Instalado"
    else
        echo "✗ NVM: No instalado"
    fi
    
    echo "=" * 50
}

# Función para mostrar información post-instalación
show_post_install_info() {
    echo ""
    print_status "Instalación completada!"
    echo ""
    echo -e "${BLUE}Comandos útiles:${NC}"
    echo ""
    
    if command -v node >/dev/null 2>&1; then
        echo "Node.js:"
        echo "  node --version          # Verificar versión"
        echo "  node app.js             # Ejecutar aplicación"
        echo ""
    fi
    
    if command -v npm >/dev/null 2>&1; then
        echo "npm:"
        echo "  npm --version           # Verificar versión"
        echo "  npm install package     # Instalar paquete"
        echo "  npm init                # Inicializar proyecto"
        echo ""
    fi
    
    if [[ -d "$HOME/.nvm" ]]; then
        echo "NVM:"
        echo "  nvm list                # Listar versiones instaladas"
        echo "  nvm install 18.17.0     # Instalar versión específica"
        echo "  nvm use 18.17.0         # Cambiar a versión específica"
        echo "  nvm alias default 18    # Establecer versión por defecto"
        echo ""
    fi
    
    if command -v pm2 >/dev/null 2>&1; then
        echo "PM2:"
        echo "  pm2 start app.js        # Iniciar aplicación"
        echo "  pm2 list                # Listar aplicaciones"
        echo "  pm2 logs                # Ver logs"
        echo "  pm2 restart app_name    # Reiniciar aplicación"
        echo "  pm2 stop app_name       # Detener aplicación"
        echo "  pm2 save                # Guardar configuración"
        echo ""
    fi
    
    echo -e "${YELLOW}Nota: Para usar NVM, reinicia tu terminal o ejecuta: source ~/.bashrc${NC}"
}

# Función para instalar Node.js con múltiples métodos
install_nodejs_auto() {
    print_status "Instalando Node.js con método automático..."
    
    # Método 1: NodeSource (recomendado)
    if install_nodejs_nodesource; then
        print_status "Node.js instalado exitosamente desde NodeSource"
        return 0
    fi
    
    print_warning "Falló instalación desde NodeSource, intentando con Snap..."
    
    # Método 2: Snap
    if install_nodejs_snap; then
        print_status "Node.js instalado exitosamente con Snap"
        return 0
    fi
    
    print_warning "Falló instalación con Snap, intentando con repositorios de Ubuntu..."
    
    # Método 3: Repositorios de Ubuntu
    if install_nodejs_ubuntu; then
        print_status "Node.js instalado exitosamente desde repositorios de Ubuntu"
        return 0
    fi
    
    print_error "No se pudo instalar Node.js con ningún método"
    return 1
}

# Función para mostrar menú de instalación
show_install_menu() {
    while true; do
        echo ""
        print_header
        echo ""
        echo "Selecciona las herramientas a instalar:"
        echo ""
        echo "1. Instalar todo (Node.js + npm + NVM + PM2)"
        echo "2. Solo Node.js y npm (versión más reciente)"
        echo "3. Solo NVM (Node Version Manager)"
        echo "4. Solo PM2 (Process Manager)"
        echo "5. Verificar instalaciones existentes"
        echo "6. Salir"
        echo ""
        
        read -p "Selecciona una opción [1-6]: " choice
        
        case $choice in
            1)
                install_all
                ;;
            2)
                install_nodejs_auto
                ;;
            3)
                install_nvm
                ;;
            4)
                install_pm2
                ;;
            5)
                verify_installations
                ;;
            6)
                print_status "Saliendo..."
                exit 0
                ;;
            *)
                print_error "Opción inválida. Selecciona 1-6."
                ;;
        esac
        
        echo ""
        read -p "Presiona [Enter] para continuar..."
    done
}

# Función para instalar todo
install_all() {
    print_status "Instalando todas las herramientas..."
    
    # Verificar sistema
    check_os
    
    # Instalar dependencias
    if ! install_dependencies; then
        print_error "Error al instalar dependencias"
        return 1
    fi
    
    # Instalar Node.js
    if ! install_nodejs_auto; then
        print_error "Error al instalar Node.js"
        return 1
    fi
    
    # Instalar NVM
    if ! install_nvm; then
        print_warning "Error al instalar NVM (opcional)"
    fi
    
    # Instalar PM2
    if ! install_pm2; then
        print_warning "Error al instalar PM2 (opcional)"
    fi
    
    # Verificar instalaciones
    verify_installations
    
    # Mostrar información
    show_post_install_info
    
    print_status "Instalación completa finalizada!"
}

# Función de ayuda
show_help() {
    echo "Instalador de Node.js Completo"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --all           Instalar todo (Node.js + npm + NVM + PM2)"
    echo "  --nodejs        Solo instalar Node.js y npm"
    echo "  --nvm           Solo instalar NVM"
    echo "  --pm2           Solo instalar PM2"
    echo "  --verify        Verificar instalaciones existentes"
    echo "  --help, -h      Mostrar esta ayuda"
    echo ""
    echo "Sin opciones: Mostrar menú interactivo"
    echo ""
    echo "Ejemplos:"
    echo "  $0              # Menú interactivo"
    echo "  $0 --all        # Instalar todo"
    echo "  $0 --nodejs     # Solo Node.js"
    echo "  $0 --verify     # Verificar instalaciones"
}

# Función principal
main() {
    # Verificar si se ejecuta como usuario normal
    if [[ $EUID -eq 0 ]]; then
        print_error "No ejecutes este script como root"
        print_error "Ejecuta como usuario normal, se usará sudo cuando sea necesario"
        exit 1
    fi
    
    # Verificar si sudo está disponible
    if ! command -v sudo >/dev/null 2>&1; then
        print_error "sudo no está disponible"
        exit 1
    fi
    
    case "${1:-}" in
        --all)
            install_all
            ;;
        --nodejs)
            check_os
            install_dependencies
            install_nodejs_auto
            verify_installations
            show_post_install_info
            ;;
        --nvm)
            install_nvm
            verify_installations
            ;;
        --pm2)
            install_pm2
            verify_installations
            ;;
        --verify)
            verify_installations
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        "")
            show_install_menu
            ;;
        *)
            echo "Opción desconocida: $1"
            echo "Use --help para ver las opciones disponibles"
            exit 1
            ;;
    esac
}

# Ejecutar función principal
main "$@" 