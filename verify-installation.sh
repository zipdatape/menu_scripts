#!/bin/bash

# Script de verificación para Setup Server Script
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
    echo -e "${BLUE}  Verificación de Instalación${NC}"
    echo -e "${BLUE}================================${NC}"
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
    
    if systemctl is-enabled "$service" >/dev/null 2>&1; then
        echo -e "✓ $description"
        return 0
    else
        echo -e "✗ $description"
        return 1
    fi
}

# Función para verificar dependencias Python
check_python_deps() {
    if python3 -c "import yaml, requests" 2>/dev/null; then
        echo -e "✓ Dependencias Python (PyYAML, requests)"
        return 0
    else
        echo -e "✗ Dependencias Python (PyYAML, requests)"
        return 1
    fi
}

# Función para verificar permisos
check_permissions() {
    local file="$1"
    local description="$2"
    
    if [[ -x "$file" ]]; then
        echo -e "✓ $description"
        return 0
    else
        echo -e "✗ $description"
        return 1
    fi
}

# Función para probar comando menu
test_menu_command() {
    if /usr/local/bin/menu --version >/dev/null 2>&1; then
        echo -e "✓ Comando 'menu' funcional"
        return 0
    else
        echo -e "✗ Comando 'menu' no funcional"
        return 1
    fi
}

# Función para verificar alias
check_aliases() {
    if [[ -f "/etc/profile.d/setup-server-aliases.sh" ]]; then
        echo -e "✓ Alias configurados"
        return 0
    else
        echo -e "✗ Alias no configurados"
        return 1
    fi
}

# Función para mostrar información del sistema
show_system_info() {
    echo
    echo -e "${BLUE}Información del Sistema:${NC}"
    echo "Sistema operativo: $(lsb_release -d | cut -f2)"
    echo "Kernel: $(uname -r)"
    echo "Arquitectura: $(uname -m)"
    echo "Python: $(python3 --version 2>/dev/null || echo 'No disponible')"
    echo "Systemd: $(systemctl --version | head -n1)"
}

# Función para mostrar información de instalación
show_installation_info() {
    echo
    echo -e "${BLUE}Información de Instalación:${NC}"
    
    if [[ -f "/opt/setup-server-script/menu.py" ]]; then
        echo "Script principal: /opt/setup-server-script/menu.py"
        echo "Tamaño: $(du -h /opt/setup-server-script/menu.py | cut -f1)"
        echo "Última modificación: $(stat -c %y /opt/setup-server-script/menu.py | cut -d' ' -f1)"
    fi
    
    if [[ -f "/usr/local/bin/menu" ]]; then
        echo "Comando: /usr/local/bin/menu"
        echo "Enlace: $(ls -la /usr/local/bin/menu | awk '{print $10, $11}')"
    fi
    
    if [[ -f "/etc/setup-server-script.conf" ]]; then
        echo "Configuración: /etc/setup-server-script.conf"
    fi
    
    if [[ -d "/backup" ]]; then
        echo "Directorio backup: /backup"
        echo "Permisos: $(stat -c %a /backup)"
    fi
}

# Función para mostrar comandos disponibles
show_available_commands() {
    echo
    echo -e "${BLUE}Comandos Disponibles:${NC}"
    echo "menu                    # Ejecutar menú principal"
    echo "menu --help             # Mostrar ayuda"
    echo "menu --status           # Mostrar estado"
    echo "menu --version          # Mostrar versión"
    echo "uninstall-setup-server  # Desinstalar completamente"
    echo
    echo -e "${BLUE}Alias Disponibles (después de source /etc/profile.d/setup-server-aliases.sh):${NC}"
    echo "update-server           # Actualizar sistema"
    echo "clean-server            # Limpiar paquetes"
    echo "check-disk              # Verificar uso de disco"
    echo "check-memory            # Verificar memoria"
    echo "check-processes         # Ver procesos (htop)"
    echo "check-services          # Ver servicios activos"
    echo "check-docker            # Ver contenedores Docker"
    echo "check-ports             # Ver puertos abiertos"
    echo "check-logs              # Ver logs del sistema"
    echo "restart-services        # Reiniciar servicios críticos"
}

# Función para mostrar próximos pasos
show_next_steps() {
    echo
    echo -e "${BLUE}Próximos Pasos:${NC}"
    echo "1. Aplicar alias: source /etc/profile.d/setup-server-aliases.sh"
    echo "2. Probar comando: sudo menu"
    echo "3. Verificar funcionalidades: sudo menu --status"
    echo "4. Configurar según necesidades: sudo nano /etc/setup-server-script.conf"
    echo
    echo -e "${YELLOW}Nota: Para usar todas las funcionalidades, ejecuta con sudo${NC}"
}

# Función principal de verificación
main_verification() {
    local errors=0
    
    print_header
    
    echo "1. Verificando archivos principales..."
    check_file "/opt/setup-server-script/menu.py" "Script principal" || ((errors++))
    check_file "/usr/local/bin/menu" "Comando global" || ((errors++))
    check_file "/etc/setup-server-script.conf" "Archivo de configuración" || ((errors++))
    check_file "/etc/profile.d/setup-server-aliases.sh" "Archivo de alias" || ((errors++))
    
    echo
    echo "2. Verificando directorios..."
    check_directory "/opt/setup-server-script" "Directorio de instalación" || ((errors++))
    check_directory "/backup" "Directorio de backup" || ((errors++))
    
    echo
    echo "3. Verificando permisos..."
    check_permissions "/usr/local/bin/menu" "Permisos de ejecución del comando" || ((errors++))
    check_permissions "/opt/setup-server-script/menu.py" "Permisos del script principal" || ((errors++))
    
    echo
    echo "4. Verificando dependencias..."
    check_python_deps || ((errors++))
    check_command "python3" "Python 3" || ((errors++))
    
    echo
    echo "5. Verificando servicio..."
    check_service "setup-server-script.service" "Servicio systemd" || ((errors++))
    
    echo
    echo "6. Verificando funcionalidad..."
    test_menu_command || ((errors++))
    check_aliases || ((errors++))
    
    echo
    echo "7. Verificando archivos adicionales..."
    check_file "/usr/local/bin/uninstall-setup-server" "Script de desinstalación" || ((errors++))
    check_file "/var/log/setup-server-script.log" "Archivo de logs" || ((errors++))
    check_file "/etc/systemd/system/setup-server-script.service" "Servicio systemd" || ((errors++))
    
    # Mostrar información
    show_system_info
    show_installation_info
    show_available_commands
    show_next_steps
    
    # Resumen final
    echo
    echo -e "${BLUE}Resumen de Verificación:${NC}"
    if [[ $errors -eq 0 ]]; then
        echo -e "${GREEN}✓ Instalación completada exitosamente${NC}"
        echo "Todos los componentes están instalados y funcionando correctamente."
    else
        echo -e "${RED}✗ Se encontraron $errors problema(s)${NC}"
        echo "Revisa los errores arriba y ejecuta: sudo ./setup-service.sh"
    fi
    
    echo
    echo -e "${BLUE}Para más información:${NC}"
    echo "Documentación: README.md, QUICK_START.md, SERVICE_SETUP.md"
    echo "Logs: /var/log/setup-server-script.log"
    echo "Configuración: /etc/setup-server-script.conf"
}

# Función para verificación rápida
quick_check() {
    echo -e "${BLUE}Verificación Rápida${NC}"
    echo "=================="
    
    local quick_errors=0
    
    # Verificaciones esenciales
    [[ -f "/usr/local/bin/menu" ]] && echo "✓ Comando menu" || { echo "✗ Comando menu"; ((quick_errors++)); }
    [[ -x "/usr/local/bin/menu" ]] && echo "✓ Permisos OK" || { echo "✗ Permisos"; ((quick_errors++)); }
    [[ -f "/opt/setup-server-script/menu.py" ]] && echo "✓ Script principal" || { echo "✗ Script principal"; ((quick_errors++)); }
    
    # Probar comando
    if /usr/local/bin/menu --version >/dev/null 2>&1; then
        echo "✓ Funcionalidad OK"
    else
        echo "✗ Funcionalidad"
        ((quick_errors++))
    fi
    
    if [[ $quick_errors -eq 0 ]]; then
        echo -e "${GREEN}Instalación OK${NC}"
        exit 0
    else
        echo -e "${RED}Problemas detectados${NC}"
        exit 1
    fi
}

# Función de ayuda
show_help() {
    echo "Script de Verificación para Setup Server Script"
    echo ""
    echo "Uso: $0 [OPCIÓN]"
    echo ""
    echo "Opciones:"
    echo "  --quick, -q    Verificación rápida"
    echo "  --help, -h     Mostrar esta ayuda"
    echo ""
    echo "Sin opciones: Verificación completa"
    echo ""
    echo "Ejemplos:"
    echo "  $0              # Verificación completa"
    echo "  $0 --quick      # Verificación rápida"
    echo "  $0 --help       # Mostrar ayuda"
}

# Procesar argumentos
case "${1:-}" in
    --quick|-q)
        quick_check
        ;;
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        main_verification
        ;;
    *)
        echo "Opción desconocida: $1"
        echo "Use --help para ver las opciones disponibles"
        exit 1
        ;;
esac 