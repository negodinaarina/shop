import datetime
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import os
from forms import AddToCart, CheckOutForm, ItemForm, LogInForm, StatusForm
from models import db, Item, Order, User, OrderItem
from random import randint
from flask_mail import Mail, Message



application = Flask(__name__)
application.permanent_session_lifetime = datetime.timedelta(days=365)
ckeditor = CKEditor(application)
application.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = os.urandom(32)
application.config['SECRET_KEY'] = SECRET_KEY
application.config['MAIL_SERVER'] = 'smtp.googlemail.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = 'dedinsideoutside@gmail.com'  # введите свой адрес электронной почты здесь
application.config['MAIL_DEFAULT_SENDER'] = 'dedinsideoutside@gmail.com'  # и здесь
application.config['MAIL_PASSWORD'] = 'ijvppwclgzseisqd'
db.init_app(application)
login_manager = LoginManager()
login_manager.init_app(application)
mail = Mail(application)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def count_cart():
    products = []
    quantity: int
    total, index, quantity = 0, 0, 0
    cart = session.get('cart')
    for it in cart:
        item = Item.query.filter_by(id=it['id']).first()
        quantity += int(it['quantity'])
        price = int(it['quantity'])*item.price
        total += price
        products.append({'title': item.title, 'id': item.id, 'price': item.price,
                         'quantity': it['quantity'], 'total': price, 'index': index})
        index += 1

    return products, total, quantity


def send_mail(recepient, subject, order_id, status):
    html = ' <h1>Номер заказа - {{order_id}} <h1><br><h2>Статус заказа - {{status}}</h2>'
    msg = Message(subject=subject, recipients=[recepient])
    msg.html = html
    mail.send(msg)


@application.route('/')
def index():
    if 'cart' not in session:
        session['cart'] = []
    items = db.session.query(Item).all()
    return render_template('index.html', items=items, current_user=current_user)


@application.route('/about')
def about():
    if 'cart' not in session:
        session['cart'] = []
    return render_template('about.html', current_user=current_user)


@application.route('/delivery')
def delivery():
    if 'cart' not in session:
        session['cart'] = []
    return render_template('about.html', current_user=current_user)


@application.route('/item/<int:id>', methods=['GET', 'POST'])
def product(id):
    if 'cart' not in session:
        session['cart'] = []
    form = AddToCart()
    item = Item.query.get(id)
    desc_list = item.description.split(';')
    l = len(desc_list)
    return render_template('product.html', current_user=current_user, item=item, desc_list=desc_list, l=l, form=form)


@application.route('/addtocart/<int:id>')
def add_to_cart(id):
    if 'cart' not in session:
        session['cart'] = []
    found = False
    if len(session['cart']) > 0:
        for item in session['cart']:
            if item['id'] == id:
                found = True
                item['quantity'] += 1
    if not found:
        session['cart'].append({'id': id, 'quantity': 1})
    session.modified = True

    return redirect(url_for('product', id=id))


@application.route('/cart', methods=['GET'])
def cart():
    if 'cart' not in session:
        session['cart'] = []
    if len(session['cart']) != 0:
        products, total, quantity = count_cart()
        is_empty = False
    else:
        products, total, quantity = [], 0, 0
        is_empty = True

    return render_template('cart.html', current_user=current_user, products=products, total=total, quantity=quantity, is_empty=is_empty)


@application.route('/remove_item/<int:index>')
def remove_item(index):
    del session['cart'][index]
    session.modified = True
    return redirect(url_for('cart'))



@application.route('/manageitems')
def manage_items():
    items = db.session.query(Item).all()
    return render_template('admin.html', items=items)


@application.route('/additem', methods=["POST", "GET"])
@login_required
def add_item():
    form = ItemForm()
    if request.method == 'POST':
        item = Item(
            title=form.title.data,
            description=form.description.data,
            photo_url=form.photo_url.data,
            price=form.price.data,
            weight=form.weight.data,
            size=form.size.data,
            in_stock=form.in_stock.data
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_item.html', form=form, current_user=current_user)


@application.route('/delete/<int:id>')
@login_required
def delete(id):
    item = Item.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('manage_items'))


@application.route('/checkout', methods=["GET", "POST"])
def check_out():
    form = CheckOutForm()
    products, total, quantity = count_cart()
    if request.method == 'POST':
        order = Order(
            reference=randint(1000000, 10000000),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            date=datetime.datetime.now(),
            status='ПРИНЯТ',
            total_sum=total
        )
        for product in products:
            order_item = OrderItem(
                quantity=product['quantity'],
                item_id=product['id']
            )
            order.items.append(order_item)
            item=Item.query.filter_by(id=product['id']).update({'in_stock':Item.in_stock - int(product['quantity'])})
            db.session.add(order)
            db.session.commit()

            session['cart'] = []
            session.modified = True
        send_mail(order.email, 'Заказ оформлен', order.reference, "ПРИНЯТ")
        return render_template('message.html')

    return render_template('checkout.html', form=form, total=total, quantity=quantity, products=products)


@application.route('/edit/<int:id>', methods=["POST", "GET"])
@login_required
def edit(id):
    item = Item.query.get(id)
    form = ItemForm(
        title=item.title,
        description=item.description,
        photo_url=item.photo_url,
        price=item.price,
        weight=item.weight,
        size=item.size,
        in_stock=item.in_stock
    )
    if request.method == 'POST':
        item.title = form.title.data
        item.description = form.description.data
        item.photo_url = form.photo_url.data
        item.price = form.price.data
        item.weight = form.weight.data
        item.size = form.size.data
        db.session.commit()
        return redirect(url_for('manage_items'))
    return render_template('add_item.html', form=form, current_user=current_user)


@application.route('/login', methods=["POST", "GET"])
def log_in():
    form = LogInForm()
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('signin.html', current_user=current_user, error="Неправильно введены данные", form=form)
    return render_template('signin.html', form=form, current_user=current_user)


@application.route('/logout')
def log_out():
    logout_user()
    return redirect(url_for('index'))


@application.route('/orders', methods=['GET', 'POST'])
def orders():
    orders = db.session.query(Order).all()
    return render_template('orders.html', orders=orders)


@application.route('/order/<int:id>', methods=["POST", "GET"])
def order(id):
    order = Order.query.get(id)
    form=StatusForm(status=order.status)
    if request.method == 'POST':
        order.status = form.status.data
        db.session.commit()
        send_mail(order.email, "СТАТУС ЗАКАЗА ИЗМЕНЕН", order.reference, order.status)
        return redirect(url_for('orders'))
    order_items = order.items
    items = []
    for order_item in order_items:
        item = Item.query.get(order_item.item_id)
        arr = [item, order_item.quantity]
        items.append(arr)
    return render_template('order.html', order=order, form=form, items=items)



