import random
from django.contrib.auth.models import User
from accounts.models import CuentaBancaria, Contacto, Transferencia

# Crear usuarios de staff
def crear_usuarios():
    usuarios = []
    nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Pedro']
    for nombre in nombres:
        user = User.objects.create_user(
            username=nombre.lower(),
            email=f'{nombre.lower()}@ejemplo.com',
            password='password.3',
            is_staff=True,  # Todos serán usuarios de staff pero no superadmin
            is_superuser=False
        )
        usuarios.append(user)
    return usuarios

# Crear cuentas bancarias para los usuarios
def crear_cuentas_bancarias(usuarios):
    cuentas = []
    for i, usuario in enumerate(usuarios):
        num_cuentas = 2 if i < 2 else 1  # Los primeros dos usuarios tendrán 2 cuentas bancarias
        for _ in range(num_cuentas):
            cuenta = CuentaBancaria.objects.create(
                numero=str(random.randint(1000000000, 9999999999)),  # Genera un número de cuenta aleatorio
                tipo=random.choice(['Ahorro', 'Corriente']),
                saldo=random.uniform(1000, 5000),  # Saldo entre 1000 y 5000
                usuario=usuario
            )
            cuentas.append(cuenta)
    return cuentas

# Crear contactos (todos serán contactos entre sí)
def crear_contactos(usuarios, cuentas):
    for usuario in usuarios:
        for cuenta in cuentas:
            if cuenta.usuario != usuario:  # No pueden agregarse a sí mismos como contactos
                Contacto.objects.create(usuario=usuario, cuenta_bancaria=cuenta)

# Crear transferencias entre las cuentas
def crear_transferencias(cuentas):
    for _ in range(10):  # Crear 10 transferencias aleatorias
        cuenta_origen = random.choice(cuentas)
        cuenta_destino = random.choice([cuenta for cuenta in cuentas if cuenta != cuenta_origen])
        monto = random.uniform(50, 500)  # Monto entre 50 y 500
        Transferencia.objects.create(
            cuenta_origen=cuenta_origen,
            cuenta_destino=cuenta_destino,
            monto=monto,
            motivo="Pago de servicios"
        )




# Ejecutar el script
def run():
    usuarios = crear_usuarios()
    cuentas = crear_cuentas_bancarias(usuarios)
    crear_contactos(usuarios, cuentas)
    crear_transferencias(cuentas)
    print("Datos de prueba creados exitosamente.")

# Ejecuta la función 'run' para llenar la base de datos
if __name__ == '__main__':
    run()
