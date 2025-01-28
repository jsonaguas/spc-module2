from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from typing import List


class Base (DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

ticket_inventory = db.Table(
    "ticket_inventory",
    Base.metadata,
    db.Column("service_ticket_id", db.ForeignKey("service_tickets.id")),
    db.Column("inventory_id", db.ForeignKey("inventory.id"))
)
ticket_mechanic = db.Table(
    "ticket_mechanic",
    Base.metadata,
    db.Column("service_ticket_id", db.ForeignKey("service_tickets.id")),
    db.Column("mechanic_id", db.ForeignKey("mechanics.id"))
)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20))
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)

    service_tickets: Mapped[List["ServiceTickets"]] = db.relationship('ServiceTickets', back_populates='customer', cascade = "all, delete")

class ServiceTickets (Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[str] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('customers.id'), nullable=False)

    customer: Mapped["Customer"] = (db.relationship(back_populates='service_tickets'))
    mechanics: Mapped[List["Mechanic"]] = db.relationship(secondary=ticket_mechanic, back_populates='service_tickets')
    inventory: Mapped[List["Inventory"]] = db.relationship('Inventory', secondary='ticket_inventory', back_populates='service_tickets')


class Mechanic (Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20))
    salary: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List["ServiceTickets"]] = db.relationship(secondary=ticket_mechanic, back_populates='mechanics')

class Inventory (Base):
    __tablename__ = 'inventory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)

    service_tickets: Mapped[List["ServiceTickets"]] = db.relationship('ServiceTickets', secondary='ticket_inventory', back_populates='inventory')


