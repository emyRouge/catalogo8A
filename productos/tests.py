from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Productos

REDUCE_STOCK_URL = "/api/products/reduce-stock/"


class ReduceStockTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.producto_a = Productos.objects.create(
            name="Producto A", precio=10.0, descripcion="desc a", stock=50
        )
        self.producto_b = Productos.objects.create(
            name="Producto B", precio=5.0, descripcion="desc b", stock=10
        )

    # --- casos exitosos ---

    def test_reduce_stock_un_producto(self):
        response = self.client.post(
            REDUCE_STOCK_URL,
            [{"id": self.producto_a.id, "cantidad": 5}],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto_a.refresh_from_db()
        self.assertEqual(self.producto_a.stock, 45)

    def test_reduce_stock_multiples_productos(self):
        response = self.client.post(
            REDUCE_STOCK_URL,
            [
                {"id": self.producto_a.id, "cantidad": 10},
                {"id": self.producto_b.id, "cantidad": 3},
            ],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto_a.refresh_from_db()
        self.producto_b.refresh_from_db()
        self.assertEqual(self.producto_a.stock, 40)
        self.assertEqual(self.producto_b.stock, 7)

    def test_reduce_stock_exacto_al_disponible(self):
        """Cantidad igual al stock disponible debe ser válida."""
        response = self.client.post(
            REDUCE_STOCK_URL,
            [{"id": self.producto_b.id, "cantidad": 10}],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto_b.refresh_from_db()
        self.assertEqual(self.producto_b.stock, 0)

    # --- validaciones de entrada ---

    def test_lista_vacia_retorna_400(self):
        response = self.client.post(REDUCE_STOCK_URL, [], format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_body_no_es_lista_retorna_400(self):
        response = self.client.post(
            REDUCE_STOCK_URL,
            {"id": self.producto_a.id, "cantidad": 1},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_item_sin_campo_id_retorna_400(self):
        response = self.client.post(
            REDUCE_STOCK_URL,
            [{"cantidad": 5}],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_item_sin_campo_cantidad_retorna_400(self):
        response = self.client.post(
            REDUCE_STOCK_URL,
            [{"id": self.producto_a.id}],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- errores de negocio ---

    def test_producto_inexistente_retorna_404(self):
        response = self.client.post(
            REDUCE_STOCK_URL,
            [{"id": 9999, "cantidad": 1}],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_stock_insuficiente_retorna_400(self):
        response = self.client.post(
            REDUCE_STOCK_URL,
            [{"id": self.producto_b.id, "cantidad": 99}],
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stock_no_se_modifica_si_un_item_falla(self):
        """Si un item de la lista falla en validación, ningún stock se modifica."""
        response = self.client.post(
            REDUCE_STOCK_URL,
            [
                {"id": self.producto_a.id, "cantidad": 1},
                {"id": 9999, "cantidad": 1},  # este falla
            ],
            format="json"
        )
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.producto_a.refresh_from_db()
        self.assertEqual(self.producto_a.stock, 50)  # sin cambios
