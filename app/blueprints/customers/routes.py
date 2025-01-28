from flask import jsonify, request
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from marshmallow import ValidationError
from app.models import db, Customer, ServiceTickets
from sqlalchemy import select, delete
from app.utils.util import encode_token, token_required
from app.extensions import cache, limiter

@customers_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    try:
        credentials = login_schema.load(request.json)
        email = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()

    if customer and customer.password == password:
        token = encode_token(customer.id)
        response = {
            "status": "success",
            "message": "Login successful",
            "token": token
        }
        return jsonify(response), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 400

@customers_bp.route('/', methods=['GET'])
@cache.cached(timeout=60)
def get_customers():
    query = select(Customer)
    customers = db.session.execute(query).scalars().all()
    return customers_schema.jsonify(customers), 200

@customers_bp.route('/my_tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    query = select(ServiceTickets).where(ServiceTickets.customer_id == customer_id)
    tickets = db.session.execute(query).scalars().all()
    return customer_schema.jsonify(tickets), 200


@customers_bp.route('/profile', methods=['GET'])
@token_required
def get_customer(customer_id):
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()
    return customer_schema.jsonify(customer), 200

@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], 
                            phone=customer_data['phone'], password=customer_data['password'])
    
    db.session.add(new_customer)
    db.session.commit()
    return customer_schema.jsonify(new_customer), 201

@customers_bp.route("/", methods=["DELETE"])
@token_required
def delete_customer(customer_id):
   query = select(Customer).where(Customer.id == customer_id)
   customer = db.session.execute(query).scalars().first()

   db.session.delete(customer)
   db.session.commit()
   return jsonify({"message": "Deleted successfully"}), 200

@customers_bp.route("/", methods=["PUT"])
@token_required
def update_customer(customer_id):
    try:
        update_customerd = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.id == customer_id)
    customer = db.session.execute(query).scalars().first()

    for field, value in update_customerd.items():
        setattr(customer, field, value)

    db.session.commit()
    return customer_schema.jsonify(customer), 200