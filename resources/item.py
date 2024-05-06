# JÁ NÃO SE UTILIZA FOI USADO NO INICIO DO CURSO # import uuid # GERA AS IDENTIFICAÇÕES DAS LOJAS
from flask import request
from flask.views import MethodView # CRIA UMA CLASSE E OS MÉTODOS DESSA ROTA DE CLASSE PARA ENDPOINTS ESPECIFICOS
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
# from db import items # IMPORTA OS "items" DA BASE DE DADOS. A PARTIR DA SECÇÃO 6 NÃO É PRECISO MAIS ESTE IMPORT POIS ESTAMOS A CRIAR JÁ A BASE DE DADOS
from schemas import ItemSchema, ItemUpdateSchema


blp = Blueprint("items", __name__, description="Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted."}

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()
        
        return item


@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()
    
    @jwt_required(fresh=True) # AGORA SÓ SE PODE CHAMAR ESTE ENDPOINT SE ENVIARMOS UM TOKEN/JWT. ISTO É UTIL PARA QUE CASO SE FAÇA ALGO ONDE SEJA NECESSÁRIO O LOGIN FEITO REQUER QUE O USER FAÇA LOGIN
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item