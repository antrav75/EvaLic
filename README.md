# EvaLic

EvaLic es una aplicación web desarrollada en Flask para evaluar ofertas en licitaciones públicas. Permite gestionar usuarios con roles (Administrador, Responsable, Participante), licitaciones, licitantes y ofertas, así como realizar el proceso de evaluación conforme a criterios y fases predefinidas. Genera informes de evaluación en HTML y garantiza la seguridad de la aplicación con CSRF, sesiones seguras y HTTPS.

## Características

- **Autenticación y roles**: Administrador, Responsable y Participante.
- **CRUD** de usuarios, licitaciones, licitantes y ofertas.
- **Gestión de fases** de evaluación y cálculo automático de puntuaciones según fórmulas.
- **Generación de informes** en HTML para cada evaluador.
- **Seguridad**: CSRFProtect (Flask-WTF) y Talisman (HTTPS, HSTS).

## Requisitos

- Python 3.7 o superior.
- SQLite (incluido en la instalación de Python).
- Paquetes Python listados en `requirements.txt`.

## Instalación

1. **Descomprimir o clonar el proyecto**  
   ```bash
   # Si lo has subido como zip:
   unzip EvaLic.zip
   cd EvaLic/EvaLic
   ```

2. **Crear y activar un entorno virtual**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno** *(opcional)*  
   - `SECRET_KEY`: clave secreta para la app (por defecto `clavesecreta`).  
   - `DATABASE`: ruta al fichero SQLite (por defecto `db_EvaLic.db` en el proyecto).

5. **Inicializar la base de datos**  
   La base de datos se crea automáticamente al arrancar la aplicación si no existe.

## Ejecución

Con el entorno virtual activo:
```bash
python app.py
```
La aplicación estará disponible en `http://127.0.0.1:5000/` (modo debug).

## Uso

- **Alta de usuarios**: desde el menú “Usuarios” (solo Administrador).  
- **Gestión de licitaciones, licitantes y ofertas**: accede a los apartados correspondientes en el menú.  
- **Evaluación**: el rol Evaluador verá sus tareas de evaluación y podrá generar informes.

Puedes acceder para gestionar los usuarios con el siguiente usuario y contraseña:

Username: admin
Contraseña: tfg_unir
---

Si tienes cualquier duda o encuentras errores, abre un _issue_ o contacta al autor de esta aplicación. 
