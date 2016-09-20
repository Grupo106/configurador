# -*- coding: utf-8 -*-
'''
Encargado de configurar los parámetros de sistema como la configuración de red,
del ancho de banda disponible y los servidores de nombre

Por razones de seguridad el script lee el archivo  temporal
`/tmp/netcop-cfg.tmp` (generado por la interfaz de usuario por el usuario sin
privilegio `www-data`) y escribe los archivos correspondientes con privilegio
de Administrador.
'''
import os
import re
import socket
import struct
import syslog
import subprocess
import configparser
from . import config
from jinja2 import Environment, PackageLoader

# Ubicacion de arhivos
# -------------------------------------------------------------------------
# archivo temporal que escribe la ui
TMP_CONFIG_FILE = '/tmp/netcop-cfg.tmp'
# archivo de configuracion de red
NETWORK_CONFIG_FILE = '/etc/network/interfaces.d/br0'
# archivo de configuracion de servidores de nombre
DNS_CONFIG_FILE = '/etc/resolv.conf'
# archivo de configuracion de netcop
NETCOP_CONFIG_FILE = '/etc/netcop/netcop.config'


def existe_archivo_temporal():
    '''
    Verifica que exista el archivo temporal creado por la UI.
    '''
    return os.path.isfile(TMP_CONFIG_FILE)


def validar(parametros):
    '''
    Valida que los parametros guardados en la configuracion temporal sean
    correctos.

    En caso de que los parametros sean incorrectos, lanza ValueError
    '''
    regex_dhcp = re.compile('^(si|no)$', flags=re.I)
    regex_ip = re.compile('^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
                          '(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    regex_velocidad = re.compile('^\d+$')
    FIELDS = (('dhcp', regex_dhcp),
              ('ip', regex_ip),
              ('mascara', regex_ip),
              ('gateway', regex_ip),
              ('dns1', regex_ip),
              ('dns2', regex_ip),
              ('subida', regex_velocidad),
              ('bajada', regex_velocidad),)
    # valida formato de los parametros
    for field, regex in FIELDS:
        if parametros.get(field) and not regex.match(parametros.get(field)):
            raise ValueError('{field} {value}: formato invalido'.format(
                field=field,
                value=parametros.get(field)
            ))
    # si se ingresa ip, se debe ingresar mascara, gateway y dns1
    if (parametros.get('ip') or parametros.get('mascara') or
            parametros.get('gateway')):
        if not (parametros.get('ip') and parametros.get('mascara') and
                parametros.get('gateway') and parametros.get('dns1')):
            raise ValueError('Si ingresa ip debe ingresar mascara, gateway y '
                             'dns1 obligatoriamente')
    # subida y bajada son obligatorios
    if not parametros.get('bajada') or not parametros.get('subida'):
        raise ValueError('bajada y subida son obligatorios')
    return True


def leer_temporal():
    '''
    Lee configuracion desde archivo temporal creado por UI y devuelve
    diccionario con los parametros leidos.
    '''
    # agrega una seccion dummy porque asi lo espera el configparser
    with open(TMP_CONFIG_FILE, 'r') as f:
        config_string = u'[netcop]\n' + f.read()
    config = configparser.ConfigParser()
    config.read_string(config_string)
    return {key: value for key, value in config.items('netcop')}


def borrar_temporal():
    '''
    Borra archivo temporal creado por UI
    '''
    return os.remove(TMP_CONFIG_FILE)


def procesar_parametros(config, parametros):
    '''
    Procesa los parametros leidos desde los archivos de configuracion.
    '''
    # defino dns1 y dns2
    if parametros.get('dns'):
        key = 'dns1' if not config.get('dns1') else 'dns2'
        config[key] = parametros['dns']
        del parametros['dns']
    # actualizo configuracion
    config.update(parametros)


def parse_cmd(command, pattern):
    '''
    Ejecuta el comando ´command´ y lo parsea con la expresion regular ´regex´.
    Devuelve objeto re.Matchcmd
    '''
    output = subprocess.check_output(command, shell=True)
    regex = re.compile(pattern)
    return regex.search(output)


def get_mascara(prefijo):
    '''
    Obtiene la mascara de subred a partir del prefijo.
    '''
    addr = 0xffffffff ^ 0xffffffff >> prefijo
    return socket.inet_ntoa(struct.pack("!I", addr))


def obtener_config_red():
    '''
    Lee la configuracion de red aplicada actualmente y devuelve diccionario
    que contiene la ip, mascara y gateway.
    '''
    # comando para obtener ip y prefijo
    IP_INFO = (
        'ip addr show primary ',
        'inet\s+(?P<ip>(\d+\.?){4})/(?P<prefijo>\d+)'
    )
    # comando para obtener gateway
    GATEWAY_INFO = (
        'ip -4 route get 8.8.8.8',
        'via\s+(?P<gateway>(\d+\.?){4})\s+dev\s+(?P<dev>\w+)'
    )
    # obtengo el gateway
    cmd, pattern = GATEWAY_INFO
    m = parse_cmd(cmd, pattern)
    data = {'gateway': m.group('gateway')}
    # obtengo ip de la interfaz principal
    cmd, pattern = IP_INFO
    m = parse_cmd(cmd + m.group('dev'), pattern)
    data['ip'] = m.group('ip')
    data['mascara'] = get_mascara(int(m.group('prefijo')))
    # devuelvo informacion de red
    return data


def obtener_config():
    '''
    Lee configuraciones actualmente aplicadas.
    '''
    regex = re.compile('''(
            bajada=(?P<bajada>\d+) |          # bajada
            subida=(?P<subida>\d+) |          # subida
            (?P<dhcp>dhcp) |                  # dhcp
            nameserver\s+(?P<dns>(\d+\.?){4}) # dns1 o dns2
        )''',
        flags=re.M | re.X
    )
    config = {}
    for path in (NETWORK_CONFIG_FILE, NETCOP_CONFIG_FILE, DNS_CONFIG_FILE):
        with open(path) as f:
            for m in regex.finditer(f.read()):
                params = {k: v for k, v in m.groupdict().items() if v}
                procesar_parametros(config, params)
                syslog.syslog(syslog.LOG_DEBUG,
                              "{0}: {1}".format(path, str(config)))
    config.update(obtener_config_red())
    # corrijo valor para dhcp
    config['dhcp'] = 'si' if config.get('dhcp') else 'no'
    syslog.syslog(syslog.LOG_DEBUG, "Config: %s" % str(config))
    return config


def aplicar_cambios():
    '''
    Solicita al sistema operativo que recargue la configuracion de red.
    '''
    retcode = subprocess.call(['systemctl', 'reload', 'networking.service'])
    if retcode != 0:
        raise RuntimeError('No se pudo recargar la configuración de red. '
                           'Verifique privilegios.')


def obtener_contexto():
    '''
    Obtiene el contexto que se le proveerá a los templates.
    '''
    contexto = leer_temporal()
    validar(contexto)
    # si no se especifica configuracion de red, utilizo la configuracion de red
    # actualmente aplicada
    if not contexto.get('dhcp') and not contexto.get('ip'):
        contexto.update(obtener_config_red())
    contexto.update(config.DATABASE)
    contexto.update(config.NETCOP)
    return contexto


def configurar():
    '''
    Escribe configuracion en los archivos correspondientes.
    '''
    FILES = (
        (NETWORK_CONFIG_FILE, 'br0.j2'),
        (DNS_CONFIG_FILE, 'resolv.conf.j2'),
        (NETCOP_CONFIG_FILE, 'netcop.config.j2'),
    )
    contexto = obtener_contexto()
    env = Environment(loader=PackageLoader(__package__))
    for path, template_name in FILES:
        template = env.get_template(template_name)
        config = template.render(**contexto)
        with open(path, 'w') as f:
            f.write(config.encode('utf-8'))
