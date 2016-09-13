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
            'ip': '1.1.1.1',
            'mascara': '255.0.0.0',
            'gateway': '1.1.1.1',
            'dns1': '1.1.1.1',
        }
        parametros['dhcp'] = 'si'
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
            'ip': '1.1.1.1',
            'mascara': '1.1.1.1',
            'gateway': '1.1.1.1',
        }
        parametros['ip'] = '256.1.1.1'
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

    def test_validar_dhcp_no(self):
        '''
        Prueba que los valores de la configuracion de red sea obligatoria
        cuando dhcp=no
        '''
        parametros = {
            'dhcp': 'no',
            'subida': '1',
            'bajada': '1',
        }
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['ip'] = '1.1.1.1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['mascara'] = '1.1.1.1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['gateway'] = '1.1.1.1'
        with self.assertRaises(ValueError):
            assert configurador.validar(parametros)
        parametros['dns1'] = '1.1.1.1'
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
