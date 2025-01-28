from app.extensions import ma
from app.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory

item_schema = InventorySchema()
items_schema = InventorySchema(many=True)

