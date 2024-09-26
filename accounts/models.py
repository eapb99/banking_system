from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone



class Token(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    generado_en = models.DateTimeField(auto_now_add=True)
    usado_en = models.DateTimeField(null=True, blank=True)
    es_valido = models.BooleanField(default=True)  # Puedes seguir usando este campo si es necesario

    def __str__(self):
        return f'Token {self.token} de {self.cliente.username}'

    def has_expired(self):
        # Verifica si el token ha expirado (es válido por 60 segundos)
        expiracion = self.generado_en + timedelta(seconds=60)
        return timezone.now() > expiracion

    def marcar_usado(self):
        # Marcar el token como usado
        self.usado_en = timezone.now()
        self.es_valido = False
        self.save()


# Modelo de cuenta bancaria
class CuentaBancaria(models.Model):
    TIPO_CUENTA = [
        ('Ahorro', 'Ahorro'),
        ('Corriente', 'Corriente')
    ]
    numero = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CUENTA)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cuentas')

    def __str__(self):
        return f'{self.numero} - {self.tipo}'


# Modelo de transferencia
class Transferencia(models.Model):
    cuenta_origen = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name='transferencias_salida')
    cuenta_destino = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name='transferencias_entrada')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=255, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transferencia de {self.cuenta_origen} a {self.cuenta_destino} por {self.monto}'


# Modelo de contactos (cuentas asociadas)
class Contacto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contactos')
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE)

    def __str__(self):
        return f'Contacto {self.usuario} - {self.cuenta_bancaria.numero}'
