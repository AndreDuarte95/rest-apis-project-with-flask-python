import os
import secrets

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST
import models

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint



def create_app(db_url=None):
    app = Flask(__name__) # ISTO CRIA UMA APLICAÇÃO FLASK, QUE PODE FAZER VÁRIAS COISAS, INCLUINDO A POSSIBILIDADE DE EXECUTAR A APLICAÇÃO
                        # QUANDO DEFINIRMOS UM ENDPOINT NESTA APP, QUE POSSA ACEITAR DADOS E DEVOLVER UMA RESPOSTA, A EXECUÇÃO DA APP DISPONIBILIZARÁ ESSES ENDPOINTS A UM CLIENTE.
                        # LOGO EXECUTAR A APLICAÇÃO É SEMPRE A COISA QUE QUEREMOS FAZER PARA USAR O FLASK. PARA ISSO, COM O TERMINAL ABERTO E COM O AMBIENTE VIRTUAL ATIVADO FAZ-SE 'flask run' NA RAIZ DA PASTA ONDE ESTÁ O API FLASK,
                        # POIS VAI PROCURAR O ARQUIVO CHAMADO "app" E DENTRO DELE A VARIÁVEL COM O NOME "app". É IMPORTANTE QUE O NOME DO FICHEIRO E DA VARIÁVEL ESTEJAM CORRETOS.
    load_dotenv()

    # OPÇOES DE CONFIGURAÇÃO
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores Rest API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db") # SE EXISTIR db_url ELE IRÁ USAR ESSE URL PASSADO COMO PARÂMETRO, CASO NÃO HAJA (=None), IRÁ UTILIZAR O URL DEFINIDO À FRENTE. SE À FRENTE HOUVER A VARIÁVEL DE AMBIENTE "DATABASE_URL" IRÁ USÁ-LA, CASO CONTRÁRIO USARÁ O QUE ESTÁ ENTRE ASPAS A SEGUIR ("sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    db.init_app(app) # INICIA A EXTENSÃO SQLALCHEMY DO FLASK, FORNECENDO-LHE A NOSSA APP FLASK PARA QUE O POSSA CONECTAR AO SQLALCHEMY
    migrate = Migrate(app, db)
    api = Api(app)

    app.config["JWT_SECRET_KEY"] = "andre" # secrets.SystemRandom().getrandbits(128)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )    

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
            401,
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed.", "error": "invalid_token"}
        ),
        401,
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    """with app.app_context():
        db.create_all() # SO SERA EXECUTADO CASO AS TABELAS AINDA NAO TENHAM SIDO CRIADAS""" # APOS INSTALAR O flask-migrate DEIXA DE SE USAR ESTAS LINHAS

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app