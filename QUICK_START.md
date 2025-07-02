# Guía de Inicio Rápido - Setup Server Script v2.0

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática
```bash
# Descargar el script de instalación
wget https://raw.githubusercontent.com/De0xyS3/menu_scripts/main/install.sh
chmod +x install.sh
sudo ./install.sh
```

### Opción 2: Instalación Manual
```bash
# Clonar repositorio
git clone https://github.com/De0xyS3/menu_scripts.git
cd menu_scripts

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar script
sudo python3 menu.py
```

## 🎯 Funcionalidades Principales

### 1. Docker Mejorado
- **Instalación automática** de las versiones más recientes
- **Consulta en tiempo real** de versiones desde GitHub
- **Configuración automática** de grupos de usuario

```bash
# En el menú: Opción 6
# Instala Docker CE y Docker Compose con las versiones más recientes
```

### 2. Usuarios SSH Avanzados
- **Creación de usuarios** con opción de permisos sudo
- **Configuración automática** de directorio .ssh
- **Generación de claves SSH** (RSA/Ed25519)
- **Configuración de claves existentes**

```bash
# En el menú: Opción 3
# Crea usuarios con todas las configuraciones necesarias
```

### 3. Plantillas Docker Compose
- **Nginx con SSL**
- **WordPress con MySQL y phpMyAdmin**
- **Nextcloud con MariaDB y Redis**

```bash
# En el menú: Opción 21
# Genera plantillas listas para usar
```

### 4. Optimización del Sistema
- **Configuración de swap** inteligente
- **Parámetros del kernel** optimizados
- **Límites del sistema** aumentados

```bash
# En el menú: Opciones 16, 17
# Optimiza el rendimiento del servidor
```

### 5. Herramientas de Monitoreo
- **htop, iotop, ncdu, glances**
- **nethogs, iftop** para monitoreo de red
- **Servicios comunes** (vim, wget, curl, tree, etc.)

```bash
# En el menú: Opciones 25, 26
# Instala herramientas esenciales
```

## 🔧 Uso Rápido

### Configuración Básica de un Servidor
1. **Zona horaria**: Opción 2
2. **Usuarios SSH**: Opción 3
3. **Docker**: Opción 6
4. **Nginx**: Opción 7
5. **PHP**: Opción 8

### Configuración de Seguridad
1. **Fail2Ban**: Opción 11
2. **UFW Firewall**: Opción 12
3. **Certbot**: Opción 13

### Optimización del Sistema
1. **Swap**: Opción 16
2. **Optimización**: Opción 17
3. **Herramientas**: Opción 25

## 🐳 Docker Compose - Ejemplos Rápidos

### WordPress
```bash
# Crear plantilla
# En el menú: Opción 21

# Usar plantilla
docker-compose -f docker-compose-wordpress.yml up -d

# Acceder a:
# WordPress: http://localhost:8080
# phpMyAdmin: http://localhost:8081
```

### Nextcloud
```bash
# Crear plantilla
# En el menú: Opción 21

# Usar plantilla
docker-compose -f docker-compose-nextcloud.yml up -d

# Acceder a: http://localhost:8080
```

## 🔍 Monitoreo Rápido

### Comandos Útiles (después de instalar alias)
```bash
check-disk      # Verificar uso de disco
check-memory    # Verificar memoria
check-processes # Ver procesos (htop)
check-services  # Ver servicios activos
update-server   # Actualizar sistema
clean-server    # Limpiar paquetes
```

## 🛡️ Seguridad Rápida

### Configuración Mínima de Seguridad
1. **Fail2Ban**: Protege contra ataques de fuerza bruta
2. **UFW**: Firewall básico con puertos 22, 80, 443
3. **Usuarios SSH**: Solo con claves SSH, sin contraseñas

### Verificar Seguridad
```bash
# Verificar servicios de seguridad
sudo systemctl status fail2ban
sudo ufw status
sudo systemctl status ssh

# Verificar logs
sudo tail -f /var/log/fail2ban.log
sudo tail -f /var/log/auth.log
```

## 📊 Backup y Mantenimiento

### Backup Automático
```bash
# En el menú: Opción 28
# Crea backup de configuraciones y bases de datos
```

### Actualización del Script
```bash
# En el menú: Opción 29
# Actualiza automáticamente el script
```

## 🚨 Solución de Problemas

### Docker no funciona después de instalar
```bash
# Cerrar sesión y volver a iniciar
logout
# O reiniciar el sistema
sudo reboot
```

### Usuario no puede usar sudo
```bash
# Verificar grupo sudo
groups $USER

# Agregar usuario al grupo sudo
sudo usermod -aG sudo $USER
```

### Problemas de red después de configurar IP estática
```bash
# Tener acceso físico al servidor
# O usar consola de recuperación
# Verificar configuración de red
sudo netplan apply
```

## 📞 Comandos de Emergencia

### Reiniciar servicios críticos
```bash
sudo systemctl restart ssh
sudo systemctl restart nginx
sudo systemctl restart mysql
sudo systemctl restart docker
```

### Verificar estado del sistema
```bash
sudo systemctl status
sudo journalctl -xe
sudo dmesg | tail
```

### Limpiar espacio en disco
```bash
sudo apt-get autoremove -y
sudo apt-get autoclean
sudo journalctl --vacuum-time=7d
```

## 🎯 Flujo de Trabajo Recomendado

### Para un Servidor Nuevo
1. **Instalar script**: `sudo ./install.sh`
2. **Configurar zona horaria**: Opción 2
3. **Crear usuarios SSH**: Opción 3
4. **Instalar Docker**: Opción 6
5. **Configurar seguridad**: Opciones 11, 12
6. **Optimizar sistema**: Opciones 16, 17
7. **Instalar herramientas**: Opciones 25, 26
8. **Crear backup**: Opción 28

### Para un Servidor Existente
1. **Actualizar script**: Opción 29
2. **Revisar seguridad**: Opciones 11, 12, 13
3. **Optimizar sistema**: Opciones 16, 17
4. **Instalar herramientas**: Opciones 25, 26
5. **Crear backup**: Opción 28

## 📚 Recursos Adicionales

- **Documentación completa**: README.md
- **Ejemplos Docker Compose**: docker-compose-examples/
- **Script de instalación**: install.sh
- **Dependencias**: requirements.txt

## 🆘 Soporte

- **Issues**: GitHub Issues
- **Documentación**: README.md
- **Ejemplos**: docker-compose-examples/
- **Logs**: `/var/log/` para debugging 