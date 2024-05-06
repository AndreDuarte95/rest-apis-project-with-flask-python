from db import db


# RELACIONAMENTO DE MUITOS PARA MUITOS
class ItemsTags(db.Model):
    __tablename__ = "items_tags"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id")) # O RELACIONAMENTO DE N PARA N ACONTECE AQUI NESTAS DUAS LINHAS, NÃO ESQUECENDO DE IR A CADA MODELO INSERIR A "RELATIONSHIP"
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"))