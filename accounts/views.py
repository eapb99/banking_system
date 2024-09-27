from decimal import Decimal
import json
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.crypto import get_random_string
from .models import Token, CuentaBancaria, Contacto, Transferencia
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generar_token(request):
    usuario_actual = request.user

    token_existente = Token.objects.filter(cliente=usuario_actual, es_valido=True).last()

    if token_existente:
        if token_existente.has_expired():
            token_existente.es_valido = False
            token_existente.save()
        else:
            tiempo_restante = 60 - (timezone.now() - token_existente.generado_en).seconds
            return Response({'token': token_existente.token, 'tiempo_restante': tiempo_restante})

    nuevo_token_valor = get_random_string(6, allowed_chars='0123456789')  # Generar token aleatorio de 6 dígitos
    nuevo_token = Token.objects.create(cliente=usuario_actual, token=nuevo_token_valor, es_valido=True)
    return Response({'token': nuevo_token.token, 'tiempo_restante': 60})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_cuenta_origen(request):
    usuario_actual = request.user
    cuentas = CuentaBancaria.objects.filter(usuario=usuario_actual)
    lista_cuentas = [{'numero': cuenta.numero, 'tipo': cuenta.tipo, 'saldo': cuenta.saldo} for cuenta in cuentas]
    return JsonResponse({'cuentas': lista_cuentas})


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Se requiere autenticación
def obtener_tokens_cliente(request):
    user = request.user
    tokens = Token.objects.filter(cliente=user)

    # Verificar cada token si sigue siendo válido
    lista_tokens = []
    for t in tokens:
        # Calcular la diferencia en segundos entre el tiempo actual y el tiempo de generación
        tiempo_actual = timezone.now()
        tiempo_generado = t.generado_en
        tiempo_diferencia = (tiempo_actual - tiempo_generado).total_seconds()

        # Si han pasado más de 60 segundos desde la generación, marcar el token como no válido
        if tiempo_diferencia > 60 and t.es_valido:
            t.es_valido = False
            t.save()

        # Añadir el token a la lista de respuesta
        lista_tokens.append({
            'token': t.token,
            'generado_en': t.generado_en.strftime("%m/%d/%Y, %H:%M:%S"),
            'usado_en': t.usado_en.strftime("%m/%d/%Y, %H:%M:%S") if t.usado_en else None,
            'es_valido': t.es_valido
        })

    return JsonResponse({'tokens': lista_tokens})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_contactos(request):
    usuario = request.user
    contactos = Contacto.objects.filter(usuario=usuario)
    lista_contactos = [{'nombre': contacto.cuenta_bancaria.usuario.username, 'numero': contacto.cuenta_bancaria.numero}
                       for contacto in contactos]
    return JsonResponse({'contactos': lista_contactos})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def realizar_transferencia(request):
    usuario_actual = request.user

    cuenta_origen_id = request.data.get('cuenta_origen')
    cuenta_destino_id = request.data.get('cuenta_destino')
    monto = Decimal(request.data.get('monto'))
    motivo = request.data.get('motivo', '')
    token_valor = request.data.get('token')

    try:
        cuenta_origen = CuentaBancaria.objects.get(numero=cuenta_origen_id, usuario=usuario_actual)
    except CuentaBancaria.DoesNotExist:
        return Response({'error': 'La cuenta de origen no existe o no pertenece al usuario'}, status=404)

    try:
        cuenta_destino = CuentaBancaria.objects.get(numero=cuenta_destino_id)
    except CuentaBancaria.DoesNotExist:
        return Response({'error': 'La cuenta de destino no existe'}, status=404)

    try:
        token = Token.objects.get(cliente=usuario_actual, token=token_valor, es_valido=True)
    except Token.DoesNotExist:
        return Response({'error': 'El token no es válido o ha expirado'}, status=400)

    if token.has_expired():
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

    token.es_valido = False
    token.usado_en = timezone.now()
    token.save()

    return Response({'mensaje': 'Transferencia realizada con éxito'})
