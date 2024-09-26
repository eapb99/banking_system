from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import CustomTokenObtainPairView

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('generarToken/<int:usuario_id>/', views.generar_token, name='generar_token'),
    path('usarToken/', views.usar_token, name='usar_token'),
    path('obtener_cuenta_origen/', views.obtener_cuenta_origen, name='obtener_cuenta_origen'),
    path('obtener_tokens_cliente/', views.obtener_tokens_cliente, name='obtener_tokens_cliente'),
    path('obtener_contactos/<int:usuario_id>/', views.obtener_contactos, name='obtener_contactos'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
