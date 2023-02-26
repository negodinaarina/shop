from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, validators, HiddenField, EmailField, SelectField
from wtforms.validators import DataRequired, Email
from flask_ckeditor import CKEditorField

class ItemForm(FlaskForm):
    title = StringField('Название товара', validators=[DataRequired()])
    description = CKEditorField('Описание товара', validators=[DataRequired()])
    photo_url = StringField('Ссылка на фотографию', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    weight = StringField('Вес', validators=[DataRequired()])
    size = StringField('Размер', validators=[DataRequired()])
    in_stock = IntegerField('Количество в наличии', validators=[DataRequired()])
    submit = SubmitField('Внести')


class LogInForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class AddToCart(FlaskForm):
    id = HiddenField('ID')
    quantity = IntegerField('Quantity')


class CheckOutForm(FlaskForm):
    first_name = StringField('Ваше имя', validators=[DataRequired()])
    last_name = StringField('Ваша фамилия', validators=[DataRequired()])
    email = EmailField('Электронная почта', validators=[DataRequired(), Email()])
    submit = SubmitField('Оплатить')

class StatusForm(FlaskForm):
    status = SelectField('Статус', choices=[('ПРИНЯТ', 'ПРИНЯТ'), ('СОБИРАЕТСЯ', 'СОБИРАЕТСЯ'), ('В ДОСТАВКЕ','В ДОСТАВКЕ'), ('ВЫПОЛНЕН','ВЫПОЛНЕН')])
    submit = SubmitField('Выбрать')