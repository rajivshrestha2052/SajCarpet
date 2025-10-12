from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views.category import CategoryViewSet
from api.views.product import ProductViewSet
from api.views.order import OrderViewSet
from api.views.customer import UserViewSet, CustomerViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'customers', CustomerViewSet, basename='customers')

urlpatterns = router.urls