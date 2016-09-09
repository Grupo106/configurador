Configurador
==================================
> Encargado de configurar los parámetros de sistema como la configuración de red, del ancho de banda disponible y los servidores de nombre

Por razones de seguridad el script lee un archivo desde el directorio temporal `/tmp` (generado por la interfaz de usuario por el usuario sin privilegio `www-data`) y escribe los archivos correspondientes con privilegio de Administrador.

Uso
----------------------------------
### Obtener parámetros de sistema
```bash
# configurador
```

Obtiene los parámetros de sistema actualmente aplicados. Devuelve una lista de lineas del tipo clave=valor. Por ejemplo:

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
Para la aplicación de los parámetros de sistema se generará una tarea en el demonio `cron` del usuario `root`

```bash
# configurador --set
```

Lista de parámetros
------------------------------------------------
Nombre de parámetro | Descripción                    | Valores válidos | Obligatorio
------------------- + ------------------------------ + --------------- + --------------------
**dhcp**            | Indica si se obtiene la        | si/SI           | Si
                    | configuración de red           | no/NO           |
                    | automaticamente desde un       |                 |
                    | servidor DHCP                  |                 |
------------------- + ------------------------------ + --------------- + --------------------
**ip**              | Dirección IPv4 del dispositivo | 192.168.1.2     | Siempre que `dchp=no`
------------------- + ------------------------------ + --------------- + --------------------
**mascara**         | Máscara de subred              | 255.255.255.0   | Siempre que `dchp=no`
------------------- + ------------------------------ + --------------- + --------------------
**gateway**         | Puerta de enlace predeterminada| 192.168.1.1     | Siempre que `dchp=no`
------------------- + ------------------------------ + --------------- + --------------------
**dns1**            | Servidor de nombres primario   | 192.168.1.1     | Siempre que `dchp=no`
------------------- + ------------------------------ + --------------- + --------------------
**dns2**            | Servidor de nombres alternativo| 192.168.1.1     | No
------------------- + ------------------------------ + --------------- + --------------------
**bajada**          | Ancho de banda de bajada       | 10              | Si
                    | (en Megabits por segundo) que  |                 |
                    | posee el enlace de Internet    |                 |
------------------- + ------------------------------ + --------------- + --------------------
**subida**          | Ancho de banda de subida       | 10              | Si
                    | (en Megabits por segundo) que  |                 |
                    | posee el enlace de Internet    |                 |
