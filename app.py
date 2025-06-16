from flask import Flask
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_talisman import Talisman
from config import Config
from models.dao import init_db, close_connection
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.licitaciones_routes import licitaciones_bp
from routes.ofertas_routes import ofertas_bp
from routes.licitantes_routes import licitantes_bp
from routes.evaluador_routes import evaluador_bp
from routes.criterios_routes import criterios_bp
from datetime import timedelta



def create_app():
    app = Flask(__name__)

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)
    
    app.config.from_object(Config)
    # Inicializa CSRFProtect
    csrf = CSRFProtect(app)

        # Forzar HTTPS y añadir HSTS
    # content_security_policy=None desactiva CSP
    Talisman(app, 
             force_https=True,
             strict_transport_security=True,
             strict_transport_security_max_age=31536000,
             content_security_policy=None)


    app.permanent_session_lifetime = timedelta(minutes=30)  # Sesión permanente por 30 minutos

    app.config.from_object(Config)

    @app.context_processor
    def utility_processor():
        from flask import request, url_for
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for('licitaciones.index', **args)
        return dict(url_for_other_page=url_for_other_page)


    # registro teardown, init_db
    app.teardown_appcontext(close_connection)
    with app.app_context():
        init_db(app)

    # blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(licitaciones_bp)
    app.register_blueprint(ofertas_bp)
    app.register_blueprint(licitantes_bp)
    app.register_blueprint(evaluador_bp)
    app.register_blueprint(criterios_bp)


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
