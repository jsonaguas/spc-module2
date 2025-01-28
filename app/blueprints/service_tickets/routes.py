from flask import jsonify, request
from . import service_tickets_bp   
from .schemas import service_ticket_schema, service_tickets_schema, edit_ticket_schema
from app.models import db, ServiceTickets, Mechanic, Inventory
from sqlalchemy import select, delete 
from marshmallow import ValidationError


@service_tickets_bp.route('/', methods=["POST"])
def create_service_ticket():
    try:
        service_ticket_data = service_ticket_schema.load(request.json)
        print(service_ticket_data)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_service_ticket = ServiceTickets(service_date = service_ticket_data["service_date"], 
                                        service_desc = service_ticket_data["service_desc"],
                                        VIN = service_ticket_data["VIN"],
                                        customer_id = service_ticket_data["customer_id"]
                                        )

    for part_id in service_ticket_data["part_ids"]:
        query = select(Inventory).where(Inventory.id == part_id)
        part = db.session.execute(query).scalar()
        if part:
            new_service_ticket.inventory.append(part)
        else:
            return jsonify({"message": "Part with id not found"}), 400
        
    for mechanic_id in service_ticket_data["mechanic_ids"]:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalar()
        if mechanic:
            new_service_ticket.mechanics.append(mechanic)
        else:
            return jsonify({"message": "Mechanic with id not found"}), 400
    
    db.session.add(new_service_ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(new_service_ticket), 201

@service_tickets_bp.route('/', methods=["GET"])
def get_service_tickets():
    query = select(ServiceTickets)
    result = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(result), 200

@service_tickets_bp.route('/<int:ticket_id>', methods=["PUT"])
def edit_ticket_mechanic(ticket_id):
    try:
        ticket_edits = edit_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    query = select(ServiceTickets).where(ServiceTickets.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()

    for mechanic_id in ticket_edits["add_mechanic_ids"]:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
        else:
            return jsonify({"message": "Mechanic with id not found"}), 400
    
    for mechanic_id in ticket_edits["remove_mechanic_ids"]:
        query = select(Mechanic).where(Mechanic.id == mechanic_id)
        mechanic = db.session.execute(query).scalars().first()
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)


    for part_id in ticket_edits["add_part_ids"]:
        query = select(Inventory).where(Inventory.id == part_id)
        part = db.session.execute(query).scalars().first()
        if part and part not in ticket.inventory:
            ticket.inventory.append(part)
        else:
            return jsonify({"message": "Part with id not found"}), 400
        

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200

@service_tickets_bp.route('/<int:ticket_id>/edit', methods=["PUT"])
def edit_ticket_part(ticket_id):
    try:
        ticket_edits2 = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    query = select(ServiceTickets).where(ServiceTickets.id == ticket_id)
    ticket2 = db.session.execute(query).scalars().first()

    for field, value in ticket_edits2.items():
        setattr(ticket2, field, value)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket2), 200


@service_tickets_bp.route('/<int:ticket_id>', methods=["DELETE"])
def delete_ticket(ticket_id):
    query = select(ServiceTickets).where(ServiceTickets.id == ticket_id)
    ticket = db.session.execute(query).scalars().first()

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Ticket {ticket_id} deleted"}), 200

