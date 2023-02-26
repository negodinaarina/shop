from flask_sqlalchemy import SQLAlchemy
from flask import session
from flask_login import UserMixin
db = SQLAlchemy()


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Text, nullable=False)
    size = db.Column(db.String, nullable=False)
    photo_url = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    orders = db.relationship('OrderItem', backref='item', lazy=True)

    def stock(self):
        if session:
            item = []
            try:
                item = session['cart']
            except:
                pass
            inde = 0
            if len(item) > 0:
                for ind, it in enumerate(item):
                    if it.get('id') == self.id:
                        inde = ind
                return self.in_stock - item[inde].get('quantity')
            else:
                return self.in_stock
        else:
            return self.in_stock


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(5))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String(50))
    date = db.Column(db.DateTime())
    status = db.Column(db.String(20))
    delivery_type = db.Column(db.String(20))
    total_sum = db.Column(db.String(20))
    items = db.relationship('OrderItem', backref='order', lazy=True)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

