# Setup Server Script - Versión Mejorada

Este script proporciona un menú interactivo completo para configurar, optimizar y mantener un servidor Ubuntu. Incluye opciones para instalar y configurar diversos servicios, gestionar seguridad, optimizar el sistema, y automatizar tareas de mantenimiento.

## 🚀 Nuevas Funcionalidades

### 🔧 Configuración Básica
- **Docker Mejorado**: Instalación automática de las versiones más recientes de Docker y Docker Compose
- **Usuarios SSH Avanzados**: Creación de usuarios con opción de permisos sudo y configuración de claves SSH
- **Gestión de Versiones**: Selección de versiones específicas para servicios como MySQL, MariaDB, Nginx, PHP, Node.js

### 🔒 Seguridad
- **Fail2Ban**: Instalación y configuración automática para proteger SSH
- **UFW Firewall**: Configuración de firewall con reglas básicas
- **Certbot**: Instalación para certificados SSL/TLS automáticos
- **Monitoreo SSH**: Logging avanzado de conexiones SSH

### ⚡ Sistema y Optimización
- **Configuración de Swap**: Configuración automática de memoria swap basada en RAM
- **Optimización del Sistema**: Parámetros del kernel y límites del sistema optimizados
- **Herramientas de Monitoreo**: Instalación de herramientas como htop, iotop, ncdu, glances
- **Servicios Comunes**: Instalación de herramientas útiles (vim, wget, curl, tree, etc.)

### 🐳 Docker y Contenedores
- **Plantillas Docker Compose**: Generación automática de plantillas para servicios comunes
  - Nginx
  - WordPress con MySQL
  - Nextcloud con MariaDB
- **Gestión de Contenedores**: Interfaz para gestionar contenedores Docker

### 📁 Servicios de Archivos
- **Samba**: Configuración de compartición de archivos Windows
- **NFS**: Configuración de compartición de archivos Linux

### 🔍 Monitoreo y Herramientas
- **Herramientas de Monitoreo**: htop, iotop, ncdu, nethogs, iftop, glances
- **Servicios Comunes**: Instalación de herramientas esenciales
- **Gestión Elasticsearch**: Administración de índices y réplicas

### 🛠️ Mantenimiento
- **Backup del Sistema**: Creación automática de backups de configuraciones y bases de datos
- **Actualización del Script**: Sistema de actualización automática

## 📋 Requisitos

- Ubuntu Server 18.04 o superior
- Python 3.6 o superior
- Acceso root o permisos sudo
- Conexión a internet para descargar paquetes

## 📦 Dependencias de Python

```bash
pip3 install -r requirements.txt
```

O instalar manualmente:
```bash
pip3 install PyYAML requests
```

## 🚀 Instalación

### Opción 1: Instalación como Servicio (Recomendada)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/De0xyS3/menu_scripts.git
   cd menu_scripts
   ```

2. Configura el script como servicio:
   ```bash
   chmod +x setup-service.sh
   sudo ./setup-service.sh
   ```

3. Verifica la instalación:
   ```bash
   ./verify-installation.sh
   ```

4. Usa el comando `menu`:
   ```bash
   sudo menu
   ```

### Opción 2: Instalación Manual

1. Clona el repositorio:
   ```bash
   git clone https://github.com/De0xyS3/menu_scripts.git
   cd menu_scripts
   ```

2. Instala las dependencias:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Ejecuta el script:
   ```bash
   sudo python3 menu.py
   ```

## 📖 Uso

### Comando Principal

Una vez instalado como servicio, puedes usar el comando `menu`:

```bash
# Ejecutar menú principal
sudo menu

# Mostrar ayuda
menu --help

# Mostrar estado
menu --status

# Mostrar versión
menu --version

# Actualizar script
sudo menu --update
```

### Alias Útiles

Después de la instalación, los siguientes alias estarán disponibles:

```bash
# Aplicar alias
source /etc/profile.d/setup-server-aliases.sh

# Comandos disponibles
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
```

### Menú Organizado

El script presenta un menú organizado en categorías:

### Configuración Básica
- Configurar multipathd
- Configurar zona horaria
- Crear usuarios SSH (con permisos sudo)
- Configurar MySQL/MariaDB
- Instalar Docker (versión más reciente)
- Instalar Nginx, PHP, Laravel, Git
- Instalar Node.js, npm, PM2 y NVM

### Seguridad
- Instalar Fail2Ban
- Configurar UFW Firewall
- Instalar Certbot para SSL/TLS
- Monitoreo SSH

### Sistema y Optimización
- Expandir disco
- Configurar memoria swap
- Optimizar sistema
- Configurar cronjobs

### Docker y Contenedores
- Gestionar contenedores Docker
- Crear plantillas Docker Compose

### Red
- Configurar IP estática
- Configurar IP virtual
- Configurar DHCP

### Servicios de Archivos
- Configurar Samba
- Configurar NFS

### Monitoreo y Herramientas
- Instalar herramientas de monitoreo
- Instalar servicios comunes
- Gestionar Elasticsearch

### Mantenimiento
- Crear backup del sistema
- Actualizar script

## 🔧 Características Técnicas

### Node.js y Herramientas de Desarrollo

#### Instalación de Node.js
El script ofrece múltiples opciones para instalar Node.js:

1. **Versión más reciente (LTS)**: Instalación automática desde NodeSource
2. **NVM**: Para gestionar múltiples versiones
3. **Versión específica**: Usando NVM para instalar cualquier versión
4. **PM2**: Process Manager para aplicaciones en producción

**Comandos útiles después de la instalación:**
```bash
# Verificar instalación
node --version
npm --version

# Con NVM
nvm list                    # Listar versiones instaladas
nvm install 18.17.0        # Instalar versión específica
nvm use 18.17.0            # Cambiar a versión específica
nvm alias default 18.17.0  # Establecer versión por defecto

# Con PM2
pm2 start app.js           # Iniciar aplicación
pm2 list                   # Listar aplicaciones
pm2 logs                   # Ver logs
pm2 restart app_name       # Reiniciar aplicación
pm2 stop app_name          # Detener aplicación
pm2 save                   # Guardar configuración
```

### Docker Mejorado
- Consulta automática de versiones más recientes desde GitHub
- Instalación desde repositorio oficial de Docker
- Script de diagnóstico completo (`docker-diagnostic.sh`)
- Script de instalación mejorado (`install-docker.sh`)
- Múltiples métodos de instalación con fallback automático
- Verificación completa de instalación
- Configuración automática de grupos de usuario
- Docker Compose con la versión más reciente

### Node.js y Herramientas de Desarrollo
- **Node.js**: Instalación de la versión más reciente desde NodeSource
- **NVM (Node Version Manager)**: Gestión de múltiples versiones de Node.js
- **npm**: Gestor de paquetes de Node.js incluido automáticamente
- **PM2**: Process Manager para aplicaciones Node.js en producción
- **Múltiples métodos de instalación**: NodeSource, Snap, repositorios de Ubuntu
- **Selección de versiones**: Instalar versiones específicas usando NVM
- **Configuración automática**: Variables de entorno y configuración de PM2

### Scripts de Diagnóstico e Instalación

#### `docker-diagnostic.sh`
Script completo de diagnóstico para Docker que incluye:
- Verificación del sistema operativo y dependencias
- Análisis de repositorios Docker
- Verificación de instalación y versiones
- Comprobación de servicios y permisos
- Pruebas de funcionalidad
- Análisis de configuración de red
- Revisión de logs del sistema
- Recomendaciones específicas para resolver problemas
- Modo de reparación automática (requiere root)

**Uso:**
```bash
# Diagnóstico completo
./docker-diagnostic.sh

# Reparación automática (requiere root)
sudo ./docker-diagnostic.sh --fix

# Mostrar ayuda
./docker-diagnostic.sh --help
```

#### `install-docker.sh`
Script de instalación mejorado con múltiples métodos de fallback:
- Verificación previa del sistema
- Instalación de dependencias
- Configuración de repositorio oficial
- Instalación de paquetes Docker
- Instalación de Docker Compose standalone
- Configuración de servicios y permisos
- Verificación completa de instalación
- Diagnóstico post-instalación
- Información de uso y documentación

**Uso:**
```bash
# Instalación completa
./install-docker.sh

# Solo diagnóstico
./install-docker.sh --diagnostic

# Mostrar ayuda
./install-docker.sh --help
```

### Usuarios SSH Avanzados
- Creación de usuarios con opción de permisos sudo
- Configuración automática de directorio .ssh
- Generación de claves SSH (RSA/Ed25519)
- Configuración de claves SSH existentes

### Optimización del Sistema
- Parámetros del kernel optimizados para servidores
- Límites del sistema aumentados
- Configuración de swap inteligente
- Optimización de red

### Plantillas Docker Compose
- Nginx con configuración SSL
- WordPress con MySQL
- Nextcloud con MariaDB
- Configuraciones listas para usar

## 🛡️ Seguridad

El script incluye múltiples capas de seguridad:
- Fail2Ban para protección contra ataques de fuerza bruta
- UFW Firewall con reglas básicas
- Configuración segura de SSH
- Certificados SSL/TLS automáticos

## 📊 Monitoreo

Herramientas de monitoreo incluidas:
- **htop**: Monitor de procesos interactivo
- **iotop**: Monitoreo de I/O
- **ncdu**: Análisis de uso de disco
- **nethogs**: Monitoreo de red por proceso
- **iftop**: Monitoreo de tráfico de red
- **glances**: Monitor de sistema completo

## 🔄 Actualizaciones

El script incluye un sistema de actualización automática que:
- Verifica actualizaciones desde el repositorio
- Descarga la versión más reciente
- Actualiza automáticamente el script

## 📝 Notas Importantes

1. **Docker**: Después de instalar Docker, es necesario cerrar sesión y volver a iniciar para que los cambios de grupo surtan efecto.

2. **Permisos**: El script debe ejecutarse con permisos de root o sudo.

3. **Backup**: Se recomienda crear un backup antes de realizar cambios importantes en el sistema.

4. **Red**: Al configurar IP estática, asegúrate de tener acceso físico al servidor en caso de problemas de conectividad.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si encuentras algún problema o tienes sugerencias:
1. Revisa los issues existentes
2. Crea un nuevo issue con detalles del problema
3. Incluye información del sistema y pasos para reproducir el problema

## 🛠️ Troubleshooting

### Problemas Comunes

1. **Error de permisos**: Asegúrate de ejecutar el script con `sudo`
2. **Dependencias faltantes**: Ejecuta `sudo apt-get update && sudo apt-get upgrade`
3. **Problemas de red**: Verifica la conectividad a internet
4. **Errores de Python**: Instala las dependencias con `pip3 install -r requirements.txt`

### Problemas Específicos de Docker

#### Error en la instalación de Docker
Si encuentras errores durante la instalación de Docker:

1. **Ejecutar diagnóstico completo:**
   ```bash
   ./docker-diagnostic.sh
   ```

2. **Intentar reparación automática:**
   ```bash
   sudo ./docker-diagnostic.sh --fix
   ```

3. **Usar script de instalación mejorado:**
   ```bash
   ./install-docker.sh
   ```

4. **Verificar manualmente:**
   ```bash
   # Verificar si Docker está instalado
   which docker
   docker --version
   
   # Verificar servicio
   sudo systemctl status docker
   
   # Verificar permisos
   groups $USER
   ls -la /var/run/docker.sock
   ```

#### Problemas de permisos de Docker
Si no puedes ejecutar Docker sin sudo:

```bash
# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Aplicar cambios (cerrar sesión y volver a iniciar)
newgrp docker

# Verificar
docker ps
```

#### Problemas de red con Docker
Si Docker no puede conectarse a internet:

```bash
# Verificar bridge Docker
ip addr show docker0

# Reiniciar Docker
sudo systemctl restart docker

# Verificar DNS
docker run busybox nslookup google.com
```

### Logs y Diagnóstico

Para diagnosticar problemas, revisa los logs del sistema:
```bash
# Ver logs del sistema
sudo journalctl -xe

# Ver logs específicos de servicios
sudo systemctl status docker
sudo systemctl status mysql
sudo systemctl status nginx

# Ver logs de Docker
sudo journalctl -u docker --no-pager -n 50
```

## 🔄 Changelog

### v2.0.0 (Mejorado)
- ✅ Instalación de Docker con versiones más recientes
- ✅ Creación de usuarios SSH con permisos sudo
- ✅ Configuración automática de claves SSH
- ✅ Plantillas Docker Compose
- ✅ Herramientas de monitoreo
- ✅ Optimización del sistema
- ✅ Configuración de swap
- ✅ Backup del sistema
- ✅ Mejor organización del menú
- ✅ Más opciones de seguridad
- ✅ **NUEVO**: Configuración como servicio systemd
- ✅ **NUEVO**: Comando global `menu`
- ✅ **NUEVO**: Alias útiles para administración
- ✅ **NUEVO**: Script de verificación de instalación
- ✅ **NUEVO**: Documentación completa del servicio
- ✅ **NUEVO**: Script de diagnóstico de Docker (`docker-diagnostic.sh`)
- ✅ **NUEVO**: Script de instalación mejorado de Docker (`install-docker.sh`)
- ✅ **NUEVO**: Múltiples métodos de instalación con fallback automático
- ✅ **NUEVO**: Sección de troubleshooting específica para Docker
- ✅ **NUEVO**: Instalación de Node.js con múltiples métodos
- ✅ **NUEVO**: NVM (Node Version Manager) para gestión de versiones
- ✅ **NUEVO**: PM2 (Process Manager) para aplicaciones Node.js
- ✅ **NUEVO**: Verificación completa de instalaciones Node.js
