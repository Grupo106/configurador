[![GitHub tag](https://img.shields.io/github/tag/Grupo106/configurador.svg?maxAge=2592000?style=plastic)](https://github.com/Grupo106/configurador/releases)
[![Build Status](https://travis-ci.org/Grupo106/configurador.svg?branch=master)](https://travis-ci.org/Grupo106/configurador)
[![Code Climate](https://codeclimate.com/github/Grupo106/configurador/badges/gpa.svg)](https://codeclimate.com/github/Grupo106/configurador)

Configurador
==================================
> Encargado de configurar los parámetros de sistema como la configuración de
> red, del ancho de banda disponible y los servidores de nombre

Por razones de seguridad el script lee el archivo  temporal
`/tmp/netcop-cfg.tmp` (generado por la interfaz de usuario por el usuario sin
privilegio `www-data`) y escribe los archivos correspondientes con privilegio
de Administrador.

Uso
----------------------------------
### Obtener parámetros de sistema
```bash
configurador
```

Obtiene los parámetros de sistema actualmente aplicados. Devuelve una lista de
lineas del tipo clave=valor. Por ejemplo:

```ini
$ configurador
ip=192.168.1.253
mascara=255.255.255.0
gateway=192.168.1.1
dns1=192.168.1.1
dns2=
bajada=20
subida=2
```

### Establecer parámetros de sistema
Para la aplicación de los parámetros de sistema se generará una tarea en el
demonio `cron` del usuario `root`

```bash
configurador --set
```

Lista de parámetros
------------------------------------------------
* **dhcp (opcional)**: Indica si se obtiene la configuración de red
  automaticamente desde un servidor DHCP. Valor por defecto: __no__
* **ip (obligatorio si `dhcp=no`)**:  Dirección IPv4 del dispositivo
* **mascara (obligatorio si `dhcp=no`)**: Máscara de subred
* **gateway (obligatorio si `dhcp=no`)**: Puerta de enlace predeterminada
* **dns1 (obligatorio si `dhcp=no`)**: Servidor de nombres primario
* **dns2 (opcional)**: Servidor de nombres alternativo
* **bajada (obligatorio)**: Ancho de banda de bajada (en Megabits por segundo)
  que posee el enlace de Internet
* **subida (obligatorio)**: Ancho de banda de subida (en Megabits por segundo)
  que posee el enlace de Internet

Ejemplos
------------------------------------------------
### Configuración por defecto
```ini
dhcp=si
bajada=1024
subida=1024
```
### Se configura la red manualmente y no se especifica valor para DHCP
```ini
ip=192.168.1.122
mascara=255.255.255.0
gateway=192.168.1.1
dns1=192.168.1.1
bajada=3
subida=0.5
```
### Se especifica la red manualmente y se explicita el parametro DHCP
```ini
dhcp=no
ip=172.16.1.254
mascara=255.255.255.0
gateway=172.16.1.1
dns1=8.8.8.8
bajada=50
subida=50
```
