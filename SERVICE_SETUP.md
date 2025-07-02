# Configuración del Servicio - Setup Server Script

## 🚀 Instalación del Servicio

### Paso 1: Configurar el Script como Servicio

```bash
# Hacer el script ejecutable
chmod +x setup-service.sh

# Ejecutar la configuración del servicio (requiere root)
sudo ./setup-service.sh
```

### Paso 2: Verificar la Instalación

```bash
# Verificar que el comando 'menu' esté disponible
which menu

# Verificar el estado del servicio
menu --status

# Verificar el servicio systemd
systemctl status setup-server-script.service
```

## 🎯 Uso del Comando `menu`

### Comandos Básicos

```bash
# Ejecutar el menú principal
menu

# Mostrar ayuda
menu --help

# Mostrar versión
menu --version

# Mostrar estado del servicio
menu --status

# Actualizar el script
menu --update

# Instalar/reinstalar
menu --install

# Desinstalar
menu --uninstall
```

### Ejemplos de Uso

```bash
# Ejecutar menú principal (requiere sudo para funcionalidades completas)
sudo menu

# Verificar estado sin privilegios
menu --status

# Actualizar el script
sudo menu --update
```

## 🔧 Configuración del Servicio

### Archivos Creados

| Archivo | Propósito |
|---------|-----------|
| `/opt/setup-server-script/menu.py` | Script principal |
| `/usr/local/bin/menu` | Comando global |
| `/etc/systemd/system/setup-server-script.service` | Servicio systemd |
| `/etc/setup-server-script.conf` | Configuración global |
| `/etc/profile.d/setup-server-aliases.sh` | Alias globales |
| `/var/log/setup-server-script.log` | Archivo de logs |
| `/usr/local/bin/uninstall-setup-server` | Script de desinstalación |

### Servicio Systemd

El servicio se crea como un servicio de tipo `oneshot` que:
- Se ejecuta al inicio del sistema
- Permanece activo después de la ejecución
- No requiere procesos en segundo plano

```bash
# Verificar estado del servicio
systemctl status setup-server-script.service

# Habilitar el servicio
systemctl enable setup-server-script.service

# Deshabilitar el servicio
systemctl disable setup-server-script.service
```

## 🛠️ Alias Útiles

Después de la instalación, los siguientes alias estarán disponibles:

### Alias del Script
```bash
menu              # Ejecutar menú principal
setup-server      # Alias alternativo
server-menu       # Alias alternativo
```

### Alias de Administración
```bash
update-server     # Actualizar sistema
clean-server      # Limpiar paquetes
check-disk        # Verificar uso de disco
check-memory      # Verificar memoria
check-processes   # Ver procesos (htop)
check-services    # Ver servicios activos
check-docker      # Ver contenedores Docker
check-ports       # Ver puertos abiertos
check-logs        # Ver logs del sistema
restart-services  # Reiniciar servicios críticos
backup-system     # Crear backup del sistema
update-script     # Actualizar el script
```

## 📋 Configuración Global

El archivo `/etc/setup-server-script.conf` contiene la configuración global:

```bash
# Ver configuración
cat /etc/setup-server-script.conf

# Editar configuración
sudo nano /etc/setup-server-script.conf
```

### Opciones de Configuración

```ini
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
```

## 🔍 Monitoreo y Logs

### Ver Logs del Script

```bash
# Ver logs en tiempo real
tail -f /var/log/setup-server-script.log

# Ver logs del sistema relacionados
journalctl -u setup-server-script.service

# Ver logs de systemd
journalctl -xe | grep setup-server
```

### Verificar Estado del Sistema

```bash
# Estado general del servicio
menu --status

# Verificar archivos importantes
ls -la /opt/setup-server-script/
ls -la /usr/local/bin/menu
ls -la /etc/setup-server-script.conf

# Verificar dependencias
python3 -c "import yaml, requests; print('Dependencias OK')"
```

## 🚨 Solución de Problemas

### Problema: Comando `menu` no encontrado

```bash
# Verificar si el archivo existe
ls -la /usr/local/bin/menu

# Si no existe, reinstalar
sudo ./setup-service.sh

# Verificar PATH
echo $PATH | grep /usr/local/bin
```

### Problema: Dependencias Python faltantes

```bash
# Instalar dependencias manualmente
pip3 install PyYAML requests

# Verificar instalación
python3 -c "import yaml, requests; print('OK')"
```

### Problema: Permisos insuficientes

```bash
# Verificar permisos
ls -la /opt/setup-server-script/menu.py
ls -la /usr/local/bin/menu

# Corregir permisos
sudo chmod +x /opt/setup-server-script/menu.py
sudo chmod +x /usr/local/bin/menu
```

### Problema: Alias no funcionan

```bash
# Recargar alias
source /etc/profile.d/setup-server-aliases.sh

# Verificar que el archivo existe
ls -la /etc/profile.d/setup-server-aliases.sh

# Reiniciar sesión
logout
# O ejecutar
exec bash
```

## 🔄 Actualización y Mantenimiento

### Actualizar el Script

```bash
# Actualizar desde el comando
sudo menu --update

# Actualizar manualmente
sudo ./setup-service.sh
```

### Backup de Configuración

```bash
# Crear backup de configuración
sudo cp /etc/setup-server-script.conf /backup/setup-server-script.conf.backup

# Restaurar configuración
sudo cp /backup/setup-server-script.conf.backup /etc/setup-server-script.conf
```

### Desinstalación Completa

```bash
# Desinstalar usando el script
sudo uninstall-setup-server

# O manualmente
sudo rm -rf /opt/setup-server-script
sudo rm -f /usr/local/bin/menu
sudo rm -f /usr/local/bin/uninstall-setup-server
sudo rm -f /etc/systemd/system/setup-server-script.service
sudo rm -f /etc/profile.d/setup-server-aliases.sh
sudo rm -f /etc/setup-server-script.conf
sudo systemctl daemon-reload
```

## 📊 Verificación de Instalación

### Script de Verificación

```bash
#!/bin/bash
echo "=== Verificación de Setup Server Script ==="

echo "1. Verificando archivos principales..."
[ -f "/opt/setup-server-script/menu.py" ] && echo "✓ Script principal" || echo "✗ Script principal"
[ -f "/usr/local/bin/menu" ] && echo "✓ Comando menu" || echo "✗ Comando menu"
[ -f "/etc/setup-server-script.conf" ] && echo "✓ Configuración" || echo "✗ Configuración"

echo "2. Verificando permisos..."
[ -x "/usr/local/bin/menu" ] && echo "✓ Permisos de ejecución" || echo "✗ Permisos de ejecución"

echo "3. Verificando dependencias..."
python3 -c "import yaml, requests" 2>/dev/null && echo "✓ Dependencias Python" || echo "✗ Dependencias Python"

echo "4. Verificando servicio..."
systemctl is-enabled setup-server-script.service >/dev/null && echo "✓ Servicio habilitado" || echo "✗ Servicio habilitado"

echo "5. Verificando alias..."
[ -f "/etc/profile.d/setup-server-aliases.sh" ] && echo "✓ Alias configurados" || echo "✗ Alias configurados"

echo "6. Probando comando..."
menu --version >/dev/null 2>&1 && echo "✓ Comando funcional" || echo "✗ Comando funcional"

echo "=== Verificación completada ==="
```

## 🎯 Flujo de Trabajo Recomendado

### Instalación Inicial
1. **Descargar scripts**: Clonar repositorio
2. **Configurar servicio**: `sudo ./setup-service.sh`
3. **Verificar instalación**: `menu --status`
4. **Aplicar alias**: `source /etc/profile.d/setup-server-aliases.sh`
5. **Probar comando**: `sudo menu`

### Uso Diario
1. **Ejecutar menú**: `sudo menu`
2. **Verificar estado**: `menu --status`
3. **Actualizar sistema**: `update-server`
4. **Monitorear**: `check-processes`, `check-disk`, `check-memory`

### Mantenimiento
1. **Actualizar script**: `sudo menu --update`
2. **Crear backup**: `sudo menu` → Opción 28
3. **Limpiar sistema**: `clean-server`
4. **Verificar logs**: `check-logs`

## 📞 Soporte

### Comandos de Emergencia

```bash
# Reiniciar servicios críticos
restart-services

# Ver logs de errores
journalctl -xe

# Verificar estado del sistema
systemctl status

# Limpiar logs antiguos
sudo journalctl --vacuum-time=7d
```

### Información del Sistema

```bash
# Información del script
menu --version
menu --status

# Información del sistema
uname -a
lsb_release -a
systemctl --version
```

### Contacto

- **Issues**: GitHub Issues
- **Documentación**: README.md, QUICK_START.md
- **Logs**: `/var/log/setup-server-script.log`
- **Configuración**: `/etc/setup-server-script.conf` 