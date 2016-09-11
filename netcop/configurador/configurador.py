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
import subprocess
import configparser

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
    pass

def recargar_red():
    '''
    Solicita al sistema operativo que recargue la configuracion de red.
    '''
    retcode = subprocess.call(['systemctl', 'reload', 'networking.service'])
    if retcode != 0:
        raise RuntimeError('No se pudo recargar la configuración de red. '
                           'Verifique privilegios.')

def configurar():
    with open(filename, "r") as sources:
	lines = sources.readlines()
    with open(filename, "w") as sources:
	for line in lines:
	    sources.write(re.sub(r'^# deb', 'deb', line))
