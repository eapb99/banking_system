import random
from decimal import Decimal

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Token, CuentaBancaria, Contacto, Transferencia
import json

from .serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        # Obtener el nombre de usuario y contraseña del cuerpo de la solicitud
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body.get('username')
        password = body.get('password')

        # Autenticación del usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Login exitoso
            return JsonResponse({'mensaje': 'Login exitoso', 'usuario_id': user.id})
        else:
            # Login fallido
            return JsonResponse({'mensaje': 'Credenciales inválidas'}, status=400)
    else:
        return JsonResponse({'mensaje': 'Método no permitido'}, status=405)


def generar_token(request, usuario_id):
    try:
        usuario = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User no encontrado'}, status=404)

    # Verificar si ya existe un token válido
    token = Token.objects.filter(cliente=usuario, es_valido=True).last()

    if token and not token.has_expired():
        # Si el token aún es válido, devolverlo con el tiempo restante
        tiempo_restante = 60 - (timezone.now() - token.generado_en).seconds
        return JsonResponse({'token': token.token, 'tiempo_restante': tiempo_restante})

    # Generar un nuevo token
    nuevo_token_valor = str(random.randint(100000, 999999))
    nuevo_token = Token.objects.create(cliente=usuario, token=nuevo_token_valor)
    return JsonResponse({'token': nuevo_token.token, 'tiempo_restante': 60})


@csrf_exempt
def usar_token(request):
    if request.method == 'POST':
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            usuario_id = body.get('usuario_id')
            token_valor = body.get('token')

            if not usuario_id or not token_valor:
                return JsonResponse({'error': 'usuario_id y token son requeridos'}, status=400)

            # Buscar el usuario
            try:
                usuario = User.objects.get(id=usuario_id)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User no encontrado'}, status=404)

            # Buscar el token
            try:
                token = Token.objects.get(cliente=usuario, token=token_valor, es_valido=True)
            except Token.DoesNotExist:
                return JsonResponse({'error': 'Token no encontrado o ya no es válido'}, status=404)

            # Verificar si el token ha expirado
            if token.has_expired():
                token.es_valido = False
                token.save()
                return JsonResponse({'error': 'Token ha expirado'}, status=400)

            # Marcar el token como usado
            token.marcar_usado()
            return JsonResponse({'mensaje': 'Token utilizado correctamente'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Error al procesar JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_cuenta_origen(request):
    usuario_actual = request.user
    cuentas = CuentaBancaria.objects.filter(usuario=usuario_actual)
    lista_cuentas = [{'numero': cuenta.numero, 'tipo': cuenta.tipo, 'saldo': cuenta.saldo} for cuenta in cuentas]
    print(lista_cuentas)
    return JsonResponse({'cuentas': lista_cuentas})


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Se requiere autenticación
def obtener_tokens_cliente(request):
    user = request.user
    tokens = Token.objects.filter(cliente=user)
    lista_tokens = [{'token': t.token, 'generado_en': t.generado_en, 'usado_en': t.usado_en, 'es_valido': t.es_valido}
                    for t in tokens]

    return JsonResponse({'tokens': lista_tokens})


def obtener_contactos(request, usuario_id):
    try:
        usuario = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User no encontrado'}, status=404)

    contactos = Contacto.objects.filter(usuario=usuario)
    lista_contactos = [{'nombre': contacto.cuenta_bancaria.usuario.username, 'numero': contacto.cuenta_bancaria.numero}
                       for contacto in contactos]

    return JsonResponse({'contactos': lista_contactos})


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # El usuario debe estar autenticado
def realizar_transferencia(request):
    # Obtener el usuario autenticado
    usuario_actual = request.user

    # Datos que vienen en el cuerpo de la solicitud
    cuenta_origen_id = request.data.get('cuenta_origen')
    cuenta_destino_id = request.data.get('cuenta_destino')
    monto = Decimal(request.data.get('monto'))
    motivo = request.data.get('motivo', '')
    token_valor = request.data.get('token')

    # Verificar que la cuenta de origen pertenezca al usuario autenticado
    try:
        cuenta_origen = CuentaBancaria.objects.get(id=cuenta_origen_id, usuario=usuario_actual)
    except CuentaBancaria.DoesNotExist:
        return Response({'error': 'La cuenta de origen no existe o no pertenece al usuario'}, status=404)

    # Verificar que la cuenta de destino exista
    try:
        cuenta_destino = CuentaBancaria.objects.get(id=cuenta_destino_id)
    except CuentaBancaria.DoesNotExist:
        return Response({'error': 'La cuenta de destino no existe'}, status=404)

    # Verificar que el token de seguridad sea válido
    try:
        token = Token.objects.get(cliente=usuario_actual, token=token_valor, es_valido=True)
    except Token.DoesNotExist:
        return Response({'error': 'El token no es válido o ha expirado'}, status=400)

    # Verificar si el token ha expirado
    if token.has_expired():
        # Si el token ha expirado, marcarlo como inválido y generar uno nuevo
        token.es_valido = False
        token.save()

        # Generar un nuevo token para el usuario
        nuevo_token = Token.objects.create(cliente=usuario_actual, token='nuevo_token_valor', es_valido=True)
        return Response({'error': 'El token ha expirado', 'nuevo_token': nuevo_token.token}, status=400)

    # Verificar que el monto sea positivo y que la cuenta tenga suficiente saldo
    if monto <= 0:
        return Response({'error': 'El monto debe ser mayor que 0'}, status=400)

    if cuenta_origen.saldo < monto:
        return Response({'error': 'Fondos insuficientes en la cuenta de origen'}, status=400)

    # Realizar la transferencia
    cuenta_origen.saldo -= monto
    cuenta_destino.saldo += monto
    cuenta_origen.save()
    cuenta_destino.save()

    # Crear el registro de la transferencia
    Transferencia.objects.create(
        cuenta_origen=cuenta_origen,
        cuenta_destino=cuenta_destino,
        monto=monto,
        motivo=motivo
    )

    # Marcar el token como usado
    token.es_valido = False
    token.usado_en = timezone.now()
    token.save()

    return Response({'mensaje': 'Transferencia realizada con éxito'})
