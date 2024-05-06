from db import db

class ItemModel(db.Model): # CLASSE ItemModel CRIADA E HERDA DO db.Model
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False) # A ForeignKey("stores.id") ESTÁ A INDICAR QUE É CHAVE ESTRANGEIRA DA TABELA stores COLUNA id
    
    store = db.relationship("StoreModel", back_populates="items")
    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags") # ESTE "back_populates=..." O QUE ESTÁ DEPOIS DO IGUAL DEVERÁ SER O MESMO NOME QUE A VARIÁVEL QUE ESTÁ NO FICHEIRO "tag.py" DOS "models" NA LINHA 11 TEM