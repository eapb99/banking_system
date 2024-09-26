from django.contrib import admin

from accounts.models import Token, CuentaBancaria, Contacto, Transferencia


# Register your models here.

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    pass


@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    pass


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    pass


@admin.register(Transferencia)
class TransferenciaAdmin(admin.ModelAdmin):
    pass