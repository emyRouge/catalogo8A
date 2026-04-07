from rest_framework import viewsets, status
from .models import Productos
from .serializers import ProductoSerializer
from rest_framework.response import Response
from rest_framework.decorators import action


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Productos.objects.all()
    serializer_class = ProductoSerializer

    @action(detail=False, methods=['POST'], url_path='reduce-stock')
    def reduce_stock(self, request):
        productos = request.data

        if not isinstance(productos, list) or len(productos) == 0:
            return Response(
                {"error": "Debes enviar una lista de productos con id y cantidad"},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in productos:
            if "id" not in item or "cantidad" not in item:
                return Response(
                    {"error": "Cada producto debe tener id y cantidad"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                producto = Productos.objects.get(id=item["id"])
            except Productos.DoesNotExist:
                return Response(
                    {"error": f"El producto con id {item['id']} no existe"},
                    status=status.HTTP_404_NOT_FOUND
                )

            if producto.stock < item["cantidad"]:
                return Response(
                    {"error": f"Stock insuficiente para el producto {producto.name}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        for item in productos:
            producto = Productos.objects.get(id=item["id"])
            producto.stock -= item["cantidad"]
            producto.save()

        return Response(
            {"message": "Stock reducido correctamente"},
            status=status.HTTP_200_OK
        )