from app import create_app
from app.models import db, Customer, ServiceTickets, Mechanic, Inventory
import unittest
from datetime import datetime

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.customer = Customer(name="test_user", email="test@gmail.com", phone="1234567890", password="mypassword")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_customer(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jdoe@gmail.com",
            "phone": "1234567890",
            "password": "mypassword"
        }
        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")

    def test_invalid_creation(self):
        customer_payload = {
            "name": "John Doe",
            "email": "jdoe@gmail.com",
            "phone": "1234567890"
        }
        response = self.client.post("/customers/", json=customer_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"password": ["Missing data for required field."]})
    
    def test_login_customer(self):
        credentials = {
            "email":"test@gmail.com",
            "password":"mypassword"
        }
        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], "success")
        return response.json['token']

    def test_invalid_login(self):
        credentials = {
            "email":"badtest@gmail.com",
            "password":"badpassword"
        }
        response = self.client.post("/customers/login", json=credentials)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "Invalid email or password"})

    def test_update_customer(self):
        update_payload = {
            "name": "Jimmy Doe",
            "email":"jimmy@gmail.com",
            "phone":"1234567890",
            "password":"newpassword"
        }
        token = self.test_login_customer()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.put("/customers/", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_invalid_update(self):
        update_payload = {
            "name": "Jimmy Doe",
            "email":"",
            "phone":"1234567890",
            "salary":"newpassword"
        }
        token = self.test_login_customer()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.put("/customers/", json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_delete_customer(self):
        token = self.test_login_customer()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.delete("/customers/", headers=headers)
        self.assertEqual(response.status_code, 200)

class TestServiceTicket(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.ticket = ServiceTickets(VIN="12345678901234567", service_date=datetime.strptime("2022-01-01", "%Y-%m-%d").date(), service_desc="Oil Change", customer_id=1)
        self.mechanic = Mechanic(name="John Doe", email="jdoe@gmail.com", phone="1234567890", salary=50000.00)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.ticket)
            db.session.add(self.mechanic)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_ticket(self):
        ticket_payload = {
            "VIN": "12345678901234567",
            "service_date": "2022-01-01",
            "service_desc": "Oil Change",
            "customer_id": 1,
            "part_ids": [],
            "mechanic_ids": []
        }
        response = self.client.post("/service_tickets/", json=ticket_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["service_desc"], "Oil Change")

    def test_invalid_create_ticket(self):
        ticket_payload = {
            "service_date": "2022-01-01",
            "service_desc": "Oil Change",
            "customer_id": 1,
            "part_ids": [],
            "mechanic_ids": []
        }
        response = self.client.post("/service_tickets/", json=ticket_payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"VIN": ["Missing data for required field."]})
    
    def test_update_ticket(self):
        update_payload = {
           "VIN": "12345678901234567",
            "service_date": "2022-02-02",
            "service_desc": "Oil Change",
            "customer_id": 1,
        }
        response = self.client.put("/service_tickets/1/edit", json=update_payload)
        self.assertEqual(response.status_code, 200)

    def add_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "jdoe@gmail.com",
            "phone": "1234567890",
            "salary": 50000.00
        }
        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "John Doe")
        return response.json["id"]


    def test_update_ticket2(self):
        update_payload = {
            "add_mechanic_ids": [1],
            "remove_mechanic_ids": [],
            "add_part_ids": []
        }
        response = self.client.put("/service_tickets/1", json=update_payload)
        self.assertEqual(response.status_code, 200)
    
    def test_delete_ticket(self):
        response = self.client.delete("/service_tickets/1")
        self.assertEqual(response.status_code, 200)

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.mechanic = Mechanic(name="John Doe", email="jdoe@gmail.com", phone="1234567890", salary=50000.00)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": "jdoe@gmail.com",
            "phone": "1234567890",
            "salary": 50000.00
        }
        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 201)
    
    def test_invalid_create_mechanic(self):
        mechanic_payload = {
            "name": "John Doe",
            "email": ""
        }
        response = self.client.post("/mechanics/", json=mechanic_payload)
        self.assertEqual(response.status_code, 400)
    
    def test_update_mechanic(self):
        update_payload = {
            "name": "Jane Doe",
            "email": "jdoe@gmail.com",
            "phone": "1234567890",
            "salary": 70000.50
        }
        response = self.client.put("/mechanics/1", json=update_payload)
        self.assertEqual(response.status_code, 200)

    def test_delete_mechanic(self):
        response = self.client.delete("/mechanics/1")
        self.assertEqual(response.status_code, 200)

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app("TestingConfig")
        self.inventory = Inventory(name="Air freshener", price=2.99)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.inventory)
            db.session.commit()
        self.client = self.app.test_client()

    def test_create_inventory(self):
        inventory_payload = {
            "name": "Air freshener",
            "price": 2.99
        }
        response = self.client.post("/inventory/", json=inventory_payload)
        self.assertEqual(response.status_code, 201)
    
    def test_invalid_create_inventory(self):
        inventory_payload = {
            "name": "Air freshener",
            "price": ""
        }
        response = self.client.post("/inventory/", json=inventory_payload)
        self.assertEqual(response.status_code, 400)
    
    def test_update_inventory(self):
        update_payload = {
            "name": "Air freshener",
            "price": 2.50
        }
        response = self.client.put("/inventory/1", json=update_payload)
        self.assertEqual(response.status_code, 200)

    def test_delete_inventory(self):
        response = self.client.delete("/inventory/1")
        self.assertEqual(response.status_code, 200)