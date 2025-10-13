from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from api.models.order import Order
from api.serializers.order import OrderSerializer
from api.views.product import StandardResultsSetPagination

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination  # reuse pagination from product.py or define here

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer__user=self.request.user)

    def perform_create(self, serializer):
        customer = self.request.user.customer
        serializer.save(customer=customer)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.is_staff and  order.status not in ['pending', 'cancelled']:
            return Response(
                {"detail": "You cannot modify an order that is processed or shipped."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.is_staff and  order.status not in ['pending', 'cancelled']:
            return Response(
                {"detail": "You cannot modify an order that is processed or shipped."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        order = self.get_object()
        if not request.user.is_staff and  order.status not in ['pending', 'cancelled']:
            return Response(
                {"detail": "You cannot delete an order that is processed or shipped."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)
