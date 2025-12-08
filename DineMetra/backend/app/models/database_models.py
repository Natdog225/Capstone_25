"""Database Models for DineMetra"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(200), nullable=False, index=True)
    category = Column(String(100), index=True)
    price = Column(Float)
    is_active = Column(Boolean, default=True)
    order_items = relationship("OrderItem", back_populates="menu_item")
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    order_timestamp = Column(DateTime, nullable=False, index=True)
    order_total = Column(Float, nullable=False)
    party_size = Column(Integer, default=1)
    order_items = relationship("OrderItem", back_populates="order")
    
    # Event features
    has_event = Column(Integer, default=0)
    event_count = Column(Integer, default=0)
    max_event_attendance = Column(Integer, default=0)
    closest_event_distance = Column(Float, default=99.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    menu_item_id = Column(
        Integer, ForeignKey("menu_items.id"), nullable=False, index=True
    )
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")
    created_at = Column(DateTime, default=datetime.utcnow)


class WaitTime(Base):
    __tablename__ = "wait_times"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    party_size = Column(Integer, nullable=False)
    actual_wait_minutes = Column(Integer, nullable=False)
    occupancy_percentage = Column(Float)
    day_of_week = Column(Integer, index=True)
    hour_of_day = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
