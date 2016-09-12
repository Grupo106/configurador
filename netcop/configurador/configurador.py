#!/usr/bin/env python
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
NETCOP_CONFIG_FILE = '/etc/netcop/netcop.conf'


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
            raise ValueError(
                '{field} {value}: formato invalido'.format(
                    field=field, value=parametros.get(field))
            )
    # si dhcp=no, se debe ingresar ip, mascara, gateway y dns1
    if not parametros.get('dhcp') or parametros['dhcp'].lower() == 'no':
        if not (parametros.get('ip') and parametros.get('mascara') and
                parametros.get('gateway') and parametros.get('dns1')):
            raise ValueError('Si dhcp=no debe ingresar ip, mascara, gateway y '
                             'dns1 obligatoriamente')
    # subida y bajada son obligatorios
    if not parametros.get('bajada') or not parametros.get('subida'):
        raise ValueError('bajada y subida son obligatorios')


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


def obtener_config():
    '''
    Lee configuraciones actualmente aplicadas e imprime resultado en formato
    clave=valor.
    '''
    regex = re.compile('(bajada=(?P<bajada>\d+)|'
                        'subida=(?P<subida>\d+)|'
                        '(?P<dhcp>dhcp)|'
                        'address (?P<ip>(\d+\.?){4})|'
                        'netmask (?P<mascara>(\d+\.?){4})|'
                        'gateway (?P<gateway>(\d+\.?){4}))', flags=re.M)

    config = dict()
    for path in (NETCOP_CONFIG_FILE, ):
        with open(path) as f:
            content = f.read()
        m = regex.search(content)
        if m:
            for x in regex.finditer(content):
                a = {k:v for k, v in x.groupdict().items() if v}
                config.update(a)
    return config


def recargar_red():
    '''
    Solicita al sistema operativo que recargue la configuracion de red.
    '''
    retcode = subprocess.call(['systemctl', 'reload', 'networking.service'])
    if retcode != 0:
        raise RuntimeError('No se pudo recargar la configuración de red. '
                           'Verifique privilegios.')


def obtener_contexto():
    '''
    Obtiene el contexto que se le pasaran a los templates.
    '''
    contexto = leer_temporal()
    validar(contexto)
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
            f.write(config)
