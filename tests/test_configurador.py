# -*- coding: utf-8 -*-
import unittest
import mock

from netcop.configurador import configurador


class ConfiguradorTests(unittest.TestCase):

    @mock.patch('os.path.isfile')
    def test_existe_archivo_temporal(self, mock):
        configurador.existe_archivo_temporal()
        mock.assert_called()

    def test_validar_dhcp(self):
        '''
        Prueba la validacion del valor de dhcp
        '''
        parametros = {
            'subida': '1',
            'bajada': '1',
            'dhcp': 'si'
        }
        assert configurador.validar(parametros)
        parametros['dhcp'] = 'SI'
        assert configurador.validar(parametros)
        parametros['dhcp'] = 'Si'
        assert configurador.validar(parametros)
        parametros['dhcp'] = 'no'
        assert configurador.validar(parametros)
        parametros['dhcp'] = 'NO'
        assert configurador.validar(parametros)
        parametros['dhcp'] = 'No'
        assert configurador.validar(parametros)
        with self.assertRaises(ValueError):
            parametros['dhcp'] = 'N0'
            configurador.validar(parametros)

    def test_validar_red_ok(self):
        '''
        Prueba la validacion de la configuracion de red (ip, mascara y gateway)
        '''
        parametros = {
            'subida': '1',
            'bajada': '1',
            'dns1': '1.1.1.1',
            'ip': '1.1.1.1',
            'mascara': '1.1.1.1',
            'gateway': '1.1.1.1',
        }
        assert configurador.validar(parametros)

    def test_validar_red_ip_fuera_rango(self):
        '''
        Prueba la validacion de la configuracion de red (ip, mascara y gateway)
        Direccion IPv4 fuera de rango
        '''
        parametros = {
            'subida': '1',
            'bajada': '1',
            'dns1': '1.1.1.1',
            'ip': '256.1.1.1',
            'mascara': '1.1.1.1',
            'gateway': '1.1.1.1',
        }
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['ip'] = '1.1.1.1'
        parametros['mascara'] = '256.1.1.1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['mascara'] = '1.1.1.1'
        parametros['gateway'] = '256.1.1.1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['gateway'] = '1.1.1.1'
        parametros['dns1'] = '256.1.1.1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['dns1'] = '1.1.1.1'
        parametros['dns2'] = '256.1.1.1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        del parametros['dns2']
        del parametros['mascara']
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)

    def test_validar_dhcp_no(self):
        '''
        Prueba que los valores de la configuracion de red sea obligatoria
        cuando dhcp=no
        '''
        parametros = {
            'subida': '1',
            'bajada': '1',
        }
        assert configurador.validar(parametros)

    def test_validar_subida_bajada(self):
        '''
        Prueba la validacion de subida y bajada que sean numeros y ademas que
        sean obligatorios.
        '''
        parametros = {
            'dns1': '1.1.1.1',
            'ip': '1.1.1.1',
            'mascara': '1.1.1.1',
            'gateway': '1.1.1.1',
        }
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['subida'] = '1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['bajada'] = '1'
        assert configurador.validar(parametros)
        parametros['subida'] = 0
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['subida'] = '0'
        parametros['bajada'] = 0
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)

    def test_leer_temporal(self):
        '''
        Prueba leer archivo temporal generado por la UI. Debe devolver un
        diccionario con los valores leidos
        '''
        mock_open = mock.mock_open(read_data='''
        dhcp=si
        subida=1024
        bajada=0
        ''')
        with mock.patch('netcop.configurador.configurador.open', mock_open):
            params = configurador.leer_temporal()
        assert params.get('dhcp') == 'si'
        assert params.get('subida') == '1024'
        assert params.get('bajada') == '0'

        mock_open = mock.mock_open(read_data='''
        dhcp=no
        subida=100
        bajada=50
        ip=192.168.1.253
        mascara=255.255.255.0
        gateway=192.168.1.1
        dns1=192.168.1.1
        ''')
        with mock.patch('netcop.configurador.configurador.open', mock_open):
            params = configurador.leer_temporal()
        assert params.get('dhcp') == 'no'
        assert params.get('subida') == '100'
        assert params.get('bajada') == '50'
        assert params.get('ip') == '192.168.1.253'
        assert params.get('mascara') == '255.255.255.0'
        assert params.get('gateway') == '192.168.1.1'
        assert params.get('dns1') == '192.168.1.1'

    @mock.patch('os.remove')
    def test_borrar_temporal(self, mock):
        '''
        Prueba borrar el archivo temporal generado por la UI
        '''
        configurador.borrar_temporal()
        mock.assert_called_with(configurador.TMP_CONFIG_FILE)

    def test_procesar_parametros(self):
        '''
        Prueba el procesamiento de parametros leidos desde el archivo temporal.
        '''
        config = {}
        configurador.procesar_parametros(config, {'ip': '1.1.1.1'})
        assert config['ip'] == '1.1.1.1'
        configurador.procesar_parametros(config, {'bajada': '10',
                                                  'subida': '1'})
        assert config['ip'] == '1.1.1.1'
        assert config['bajada'] == '10'
        assert config['subida'] == '1'

    def test_procesar_parametros_dns(self):
        '''
        Prueba el procesamiento de parametros leidos desde el archivo temporal.

        Procesamiento de dns1 y dns2
        '''
        config = {}
        configurador.procesar_parametros(config, {'dns': '1.1.1.1'})
        assert config['dns1'] == '1.1.1.1'
        configurador.procesar_parametros(config, {'dns': '2.2.2.2'})
        assert config['dns1'] == '1.1.1.1'
        assert config['dns2'] == '2.2.2.2'
        configurador.procesar_parametros(config, {'dns': '3.3.3.3'})
        assert config['dns1'] == '1.1.1.1'
        assert config['dns2'] == '3.3.3.3'

    def test_procesar_parametros_dhcp(self):
        '''
        Prueba el procesamiento de parametros leidos desde el archivo temporal.

        Correcion de valor de dhcp
        '''
        config = {}
        configurador.procesar_parametros(config, {'dhcp': 'dhcp'})
        assert config['dhcp'] == 'si'
        configurador.procesar_parametros(config, {})
        assert config['dhcp'] == 'no'

    def test_obtener_parametros_netcop(self):
        '''
        Prueba la lectura de parametros desde /etc/netcop/netcop.config
        '''
        mock_open = mock.mock_open(read_data='''
        [netcop]
        velocidad_bajada=22
        velocidad_subida=11
        inside=eth1
        outside=eth0
        ''')
        with mock.patch('netcop.configurador.configurador.open', mock_open):
            config = configurador.obtener_config()
        assert config['bajada'] == '22'
        assert config['subida'] == '11'
        mock_open.assert_any_call(configurador.NETCOP_CONFIG_FILE)

    @mock.patch('subprocess.check_output')
    def test_obtener_parametros_network(self, mock_output):
        '''
        Prueba la lectura de parametros de configuracion de red actuamente
        aplicada.
        '''
        mock_open = mock.mock_open()
        mock_output.return_value = '''
        7: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state
        UP group default
            link/ether 52:54:00:57:39:99 brd ff:ff:ff:ff:ff:ff
            inet 172.18.124.189/25 brd 172.18.124.255 scope global br0
            valid_lft forever preferred_lft forever

        8.8.8.8 via 172.18.124.129 dev br0  src 172.18.124.189
            cache
        '''
        with mock.patch('netcop.configurador.configurador.open', mock_open):
            config = configurador.obtener_config()
        assert config['ip'] == '172.18.124.189'
        assert config['mascara'] == '255.255.255.128'
        assert config['gateway'] == '172.18.124.129'
        mock_open.assert_any_call(configurador.NETWORK_CONFIG_FILE)
        mock_output.assert_called()

    def test_obtener_parametros_dhcp(self):
        '''
        Prueba la lectura de parametros de configuracion de red cuando este
        activado el dhcp
        '''
        mock_open = mock.mock_open(read_data='''
        iface br0 inet dhcp
            bridge_ports eth0 eth1
        ''')
        with mock.patch('netcop.configurador.configurador.open', mock_open):
            config = configurador.obtener_config()
        assert config['dhcp'] == 'si'
        mock_open.assert_any_call(configurador.NETWORK_CONFIG_FILE)

    def test_obtener_parametros_dns(self):
        '''
        Prueba la lectura de parametros de configuracion de dns
        '''
        mock_open = mock.mock_open(read_data='''
        nameserver 200.67.222.222
        nameserver 200.67.220.220
        ''')
        with mock.patch('netcop.configurador.configurador.open', mock_open):
            config = configurador.obtener_config()
        assert config['dns1'] == '200.67.222.222'
        assert config['dns2'] == '200.67.220.220'
        mock_open.assert_any_call(configurador.DNS_CONFIG_FILE)

    @mock.patch('subprocess.call')
    def test_aplicar_cambios(self, mock_call):
        '''
        Prueba la aplicacion de cambios de configuracion.
        '''
        mock_call.return_value = 0
        configurador.aplicar_cambios()
        mock_call.assert_called_with(['systemctl', 'reload',
                                      'networking.service'])

    @mock.patch('subprocess.call')
    def test_aplicar_cambios_error(self, mock_call):
        '''
        Prueba el tratamiento de errores al aplicar los cambios de
        configuracion.
        '''
        mock_call.return_value = 1
        with self.assertRaises(RuntimeError):
            configurador.aplicar_cambios()
        mock_call.assert_called_with(['systemctl', 'reload',
                                      'networking.service'])

    @mock.patch('netcop.configurador.configurador.obtener_config_red')
    @mock.patch('netcop.configurador.configurador.leer_temporal')
    @mock.patch('netcop.configurador.configurador.validar')
    def test_obtener_contexto_con_config_red(self, mock_validar, mock_leer,
                                             mock_config_red):
        '''
        Prueba la funcion que provee el contexto a los templates.
        '''
        # con ip dinamica
        mock_leer.return_value = {'dhcp': 'si'}
        assert configurador.obtener_contexto()
        mock_leer.assert_called()
        mock_validar.assert_called()
        mock_config_red.assert_not_called()
        # con ip fija
        mock_leer.return_value = {
            'ip': '1.1.1.1',
            'mascara': '255.0.0.0',
            'gateway': '1.0.0.1'
        }
        assert configurador.obtener_contexto()
        mock_leer.assert_called()
        mock_validar.assert_called()
        mock_config_red.assert_not_called()

    @mock.patch('netcop.configurador.configurador.obtener_config_red')
    @mock.patch('netcop.configurador.configurador.leer_temporal')
    @mock.patch('netcop.configurador.configurador.validar')
    def test_obtener_contexto_sin_config_red(self, mock_validar, mock_leer,
                                             mock_config_red):
        '''
        Prueba la funcion que provee el contexto a los templates cuando no se
        brinda configuracion de red.
        '''
        mock_leer.return_value = {}
        assert configurador.obtener_contexto()
        mock_leer.assert_called()
        mock_validar.assert_called()
        mock_config_red.assert_called()

    @mock.patch('netcop.configurador.configurador.obtener_contexto')
    def test_configurar(self, mock_contexto):
        '''
        Prueba la funcion que provee el contexto a los templates.
        '''
        mock_contexto.return_value = {}
        mock_open = mock.mock_open()
        with mock.patch('netcop.configurador.configurador.open', mock_open):
            configurador.configurar()
        mock_contexto.assert_called()
        mock_open.assert_any_call(configurador.NETCOP_CONFIG_FILE, 'w')
        mock_open.assert_any_call(configurador.NETWORK_CONFIG_FILE, 'w')
        mock_open.assert_any_call(configurador.DNS_CONFIG_FILE, 'w')

    def test_get_mascara(self):
        '''
        Prueba la funcion que transforma el prefijo en una mascara de subred.
        '''
        assert configurador.get_mascara(8) == '255.0.0.0'
        assert configurador.get_mascara(17) == '255.255.128.0'
        assert configurador.get_mascara(21) == '255.255.248.0'
        assert configurador.get_mascara(24) == '255.255.255.0'
