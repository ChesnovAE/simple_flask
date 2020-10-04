from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from cloudipsp import Api, Checkout


# Объект приложения (сайта). Создается один раз
app = Flask(__name__)
# Подрубаем базу данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app=app)

# Создаем таблицу в базе данных
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.title


# отслеживание url адресов
@app.route('/')
def index():
    # Получаем данные из таблицы
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)


@app.route('/buy/<int:id_>')
def item_buy(id_):
    item = Item.query.get(id_)

    api = Api(merchant_id=1396424, secret_key='test')
    checkout = Checkout(api=api)
    data = {
        'currency': 'USD',
        'amount': str(item.price) + '00'
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        description = request.form['description']

        item = Item(title=title, price=price, description=description)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Something went wrong"
    else:
        return render_template('create.html')


# Запускаем проект
if __name__ == '__main__':
    app.run(debug=True)
