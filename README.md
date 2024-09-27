
# Sistema de Cuentas Bancarias con Transferencias y Token Virtual

Este sistema de cuentas bancarias fue desarrollado utilizando Django,DjangoRestFramework y PostgreSQL. Implementa un mecanismo de generación y uso de tokens virtuales para garantizar la seguridad en las transferencias. A continuación, se describe el entorno de desarrollo, instalación y ejecución del sistema.

## Descripción

Este sistema web permite la gestión de cuentas bancarias, con la opción de realizar transferencias seguras utilizando un **token virtual**. Cada token es un código de seis dígitos generado de manera aleatoria y se renueva cada 60 segundos. Además, el sistema permite:

- La creación de usuarios y su asociación con los tokens generados.
- La generación de tokens y su almacenamiento en la base de datos.
- La validación de tokens en transferencias para asegurar la autenticidad del usuario.

## Requisitos

- **Lenguaje de programación**: Python (Django)
- **Base de datos**: PostgreSQL
- **Sistema de autenticación**: JWT (JSON Web Tokens)
- **Herramientas adicionales**: Postman para probar las API de generación y validación de tokens.

## Instalación

### 1. Clonar el repositorio

Clona el repositorio en tu máquina local:

```bash
git clone https://github.com/eapb99/banking_system.git
cd banking_system
```

### 2. Crear y activar un entorno virtual

Es recomendable crear un entorno virtual para el proyecto:

```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

Instala todas las dependencias necesarias listadas en el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Configura PostgreSQL para que Django pueda conectarse a la base de datos. Actualiza las credenciales de la base de datos en el archivo `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nombre_de_la_base_de_datos',
        'USER': 'usuario',
        'PASSWORD': 'contraseña',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Migrar el esquema de la base de datos

Ejecuta las migraciones para configurar el esquema de la base de datos:

```bash
python manage.py migrate
```

### 6. Poblar la base de datos

Ejecuta el script `populate_db.py` para poblar la base de datos con datos de prueba:

```bash
python manage.py shell
```
Luego dentro de la consola interactiva, importa y ejectua el script:

```python
from populate_db import run
run()
```

### 7. Crear un superusuario (Opcional)

Crea un superusuario para acceder al panel de administración de Django:

```bash
python manage.py createsuperuser
```

### 8. Ejecutar el servidor

Inicia el servidor de desarrollo de Django:

```bash
python manage.py runserver
```

Accede a la aplicación desde tu navegador en `http://127.0.0.1:8000/`.

## Endpoints principales
Todos los endpoints deben llevar en los headers el JWT token generado al hacer login para poder acceder a ellos.

1. **Generar token**: Genera un nuevo token o devuelve el actual si aún es válido.

   - Endpoint: `/generarToken/`
   - Método: GET

2. **Transferencias**: Permite realizar una transferencia entre cuentas utilizando un token válido.

   - Endpoint: `/transferencia/`
   - Método: POST
   - Parámetros: cuenta origen, cuenta destino, monto, token, monto, motivo

## Funcionalidades

- **Transferencias seguras**: Realización de transferencias entre cuentas usando el token virtual.
- **Autogeneración de tokens**: Los tokens se generan automáticamente y expiran cada 60 segundos.
- **Panel administrativo**: A través del panel de Django, los administradores pueden ver las cuentas, usuarios y registros de tokens.

## Pruebas

Para probar los endpoints del sistema, se puede utilizar Postman. Importa la colección de ejemplos desde el archivo `postman_collection.json` y realiza las solicitudes de prueba para verificar el correcto funcionamiento de las transferencias y la validación de tokens.
