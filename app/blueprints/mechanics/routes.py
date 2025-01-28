from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete
from flask_marshmallow import Marshmallow
from app.blueprints.mechanics import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema
from app.models import db, Mechanic
from marshmallow import ValidationError


@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
        print(mechanic_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    new_mechanic = Mechanic(name=mechanic_data["name"], email=mechanic_data["email"], phone=mechanic_data["phone"],
                            salary=mechanic_data["salary"])
    db.session.add(new_mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(new_mechanic), 201

@mechanics_bp.route("/", methods=["GET"])
def get_mechanics():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Mechanic)
        mechanics = db.paginate(query, page=page, per_page=per_page)
        return mechanics_schema.jsonify(mechanics), 200
    except:
        query = select(Mechanic)
        result = db.session.execute(query).scalars().all()
        return mechanics_schema.jsonify(result), 200

@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
def update_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    print (mechanic)

    if mechanic == None:
        return jsonify({"message": f"Mechanic with id {mechanic_id} not found"}), 404
    
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for field, value in mechanic_data.items():
        setattr(mechanic, field, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200

@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
def delete_mechanic(mechanic_id):
    query = select(Mechanic).where(Mechanic.id == mechanic_id)
    mechanic = db.session.execute(query).scalars().first()
    db.session.delete(mechanic)
    db.session.commit() 

    return jsonify({"message": "Mechanic deleted"}), 200

@mechanics_bp.route("/popular", methods=["GET"])
def popular_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    mechanics.sort(key=lambda mechanic:len(mechanic.service_tickets), reverse=True)
    return mechanics_schema.jsonify(mechanics), 200



    