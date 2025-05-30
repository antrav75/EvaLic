from flask import Flask
from config import Config
from models.dao import init_db, close_connection
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.licitaciones_routes import licitaciones_bp
from routes.ofertas_routes import ofertas_bp
from routes.licitantes_routes import licitantes_bp
from routes.evaluador_routes import evaluador_bp
from routes.criterios_routes import criterios_bp

def create_app():
    app = Flask(__name__)


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
