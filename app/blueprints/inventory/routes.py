from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import item_schema, items_schema
from marshmallow import ValidationError
from app.models import db, Inventory
from sqlalchemy import select, delete
from app.utils.util import encode_token, token_required


@inventory_bp.route('/', methods=['GET'])
def get_items():
    query = select(Inventory)
    items = db.session.execute(query).scalars().all()
    return items_schema.jsonify(items), 200


@inventory_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    query = select(Inventory).where(Inventory.id == item_id)
    item = db.session.execute(query).scalars().first()
    return item_schema.jsonify(item), 200


@inventory_bp.route("/", methods=["POST"])
def create_item():
    try:
        item_data = item_schema.load(request.json)
        print(item_data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_item = Inventory(name=item_data["name"], price=item_data["price"])
    db.session.add(new_item)
    db.session.commit()
    return item_schema.jsonify(new_item), 201


@inventory_bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    query = select(Inventory).where(Inventory.id == item_id)
    item = db.session.execute(query).scalars().first()

    if item == None:
        return jsonify({"message": f"Item with id {item_id} not found"}), 404

    try:
        item_data = item_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    for field, value in item_data.items():
        setattr(item, field, value)

    db.session.commit()
    return item_schema.jsonify(item), 200

@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    query = select(Inventory).where(Inventory.id == item_id)
    item = db.session.execute(query).scalars().first()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"}), 200

