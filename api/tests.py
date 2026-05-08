from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from clientes.models import Cliente
from rutas.models import Ruta
from empleados.models import Empleado
from envios.models import Encomienda
from config.choices import EstadoGeneral, EstadoEncomienda


class EncomiendaAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='12345678', password='testpass')
        self.employee = Empleado.objects.create(dni='12345678', nombres='Juan', apellidos='Perez', cargo='Gestor')

        self.remitente = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='11111111',
            nombres='Ana',
            apellidos='Lopez',
            telefono='987654321',
            email='ana@example.com',
            direccion='Calle Falsa 123',
            estado=EstadoGeneral.ACTIVO,
        )
        self.destinatario = Cliente.objects.create(
            tipo_doc='DNI',
            nro_doc='22222222',
            nombres='Luis',
            apellidos='Garcia',
            telefono='999999999',
            email='luis@example.com',
            direccion='Avenida Siempre Viva 742',
            estado=EstadoGeneral.ACTIVO,
        )
        self.ruta = Ruta.objects.create(origen='Lima', destino='Cusco', precio=50)
        self.encomienda = Encomienda.objects.create(
            codigo='ENC-100',
            descripcion='Prueba',
            peso=2.5,
            remitente=self.remitente,
            destinatario=self.destinatario,
            ruta=self.ruta,
        )

    def authenticate(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': '12345678', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        return response.data

    def test_get_token(self):
        response = self.client.post(reverse('token_obtain_pair'), {'username': '12345678', 'password': 'testpass'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], '12345678')

    def test_list_encomiendas(self):
        self.authenticate()
        response = self.client.get(reverse('encomienda-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['results']) >= 1)

    def test_detail_encomienda(self):
        self.authenticate()
        response = self.client.get(reverse('encomienda-detail', args=[self.encomienda.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['codigo'], 'ENC-100')

    def test_create_encomienda_valid(self):
        self.authenticate()
        data = {
            'codigo': 'ENC-101',
            'descripcion': 'Envio prueba',
            'peso': 3.0,
            'remitente_id': self.remitente.pk,
            'destinatario_id': self.destinatario.pk,
            'ruta_id': self.ruta.pk,
        }
        response = self.client.post(reverse('encomienda-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['codigo'].startswith('ENC-'))

    def test_create_encomienda_invalid_peso(self):
        self.authenticate()
        data = {
            'codigo': 'ENC-102',
            'descripcion': 'Envio invalido',
            'peso': 0,
            'remitente_id': self.remitente.pk,
            'destinatario_id': self.destinatario.pk,
            'ruta_id': self.ruta.pk,
        }
        response = self.client.post(reverse('encomienda-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('peso', response.data['details'])

    def test_create_encomienda_same_remitente_destinatario(self):
        self.authenticate()
        data = {
            'codigo': 'ENC-103',
            'descripcion': 'Envio duplicado',
            'peso': 1.5,
            'remitente_id': self.remitente.pk,
            'destinatario_id': self.remitente.pk,
            'ruta_id': self.ruta.pk,
        }
        response = self.client.post(reverse('encomienda-list'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cambiar_estado(self):
        self.authenticate()
        url = reverse('encomienda-cambiar-estado', args=[self.encomienda.pk])
        response = self.client.post(
            url,
            {
                'estado': EstadoEncomienda.ENTREGADA,
                'observacion': 'Cambio desde test'
            },
            format='json'
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            f"Expected 200 but got {response.status_code}: {response.data}"
        )
        self.assertEqual(response.data['estado'], EstadoEncomienda.ENTREGADA)
