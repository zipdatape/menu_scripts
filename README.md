# Setup Server Script - Versión Mejorada

Este script proporciona un menú interactivo completo para configurar, optimizar y mantener un servidor Ubuntu. Incluye opciones para instalar y configurar diversos servicios, gestionar seguridad, optimizar el sistema, y automatizar tareas de mantenimiento.

## 🚀 Nuevas Funcionalidades

### 🔧 Configuración Básica
- **Docker Mejorado**: Instalación automática de las versiones más recientes de Docker y Docker Compose
- **Usuarios SSH Avanzados**: Creación de usuarios con opción de permisos sudo y configuración de claves SSH
- **Gestión de Versiones**: Selección de versiones específicas para servicios como MySQL, MariaDB, Nginx, PHP

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

### Docker Mejorado
- Consulta automática de versiones más recientes desde GitHub
- Instalación desde repositorio oficial de Docker
- Configuración automática de grupos de usuario
- Docker Compose con la versión más reciente

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
