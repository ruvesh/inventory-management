from operator import or_, and_
from flask import Flask, render_template, request, redirect, flash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask.helpers import url_for
from flask_login.utils import login_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_login import LoginManager, login_manager, UserMixin, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
if os.environ.get('ENV') == 'production':
    app.secret_key = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://','postgressql://')
else:
    app.secret_key = 'developmentkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/inventory'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ROWS_PER_PAGE=10


# DB Models

class Stock(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    itemCode=db.Column(db.String(30), nullable=False)
    itemName=db.Column(db.String(80), nullable=False)
    stockSize=db.Column(db.Integer, nullable=False)
    entryTime=db.Column(db.DateTime)
    expiryDate=db.Column(db.DateTime, nullable=False)

    def __repr__(self) -> str:
        return self.itemCode + " " + self.itemName + " of quantity " + str(self.stockSize) + " expires on " + str(self.expiryDate) 

class User(db.Model):
    userid=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String, nullable=False, unique=True)
    role_level=db.Column(db.Integer, default=0)
    password=db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return "{ \"userid\": " + str(self.userid) + ", \"username\":  \"" + str(self.username) + "\", \"role_level\": " + str(self.role_level) + "}"


# Login and Session 

login_manager = LoginManager()
login_manager.init_app(app)


def get_requesting_user(username):
    users=User.query.all()
    for user in users:
        if username == user.username:
            return user

class RequestedUser(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username is None or username == "":
        return
    user = RequestedUser()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    requesting_user=get_requesting_user(username)
    if requesting_user is None or username is None or username == "":
        return
    user = RequestedUser()
    user.id = username
    
    
    user.is_authenticated = request.form.get('password') == requesting_user.password

    return user

@login_manager.unauthorized_handler
def unauthorized():
    flash("Please Login to access this resource.", "info")
    return redirect(url_for('login'))


    
# Routes

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        requesting_user=get_requesting_user(username)
        if requesting_user is None:
            flash("Invalid Account! User doesn't exist!", "error")
            return redirect(url_for('login'))

        if request.form['password'] == requesting_user.password:
            user = RequestedUser()
            user.id = username
            login_user(user)
            flash("Authenticated")
            return redirect(url_for('inventory'))
        flash("Invalid Credentials! Access Denied!", "error")
        return redirect(url_for('login'))
    elif request.method == 'GET':
        if current_user.is_authenticated:
            flash("Already Logged in", "info")
            return redirect(url_for('inventory'))
        return render_template('login.html')
    

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Commenting to hide incomplete dashboard

# @app.route('/')
# @login_required
# def dashboard():
#     return render_template('index.html')

@app.route('/stock', methods= ['POST', 'GET'])
@login_required
def stock():

    if request.method == 'POST':
        itemCode=request.form['itemCode']
        itemName=request.form['itemName']
        stockSize=request.form['stockSize']
        expiryDate=datetime.strptime(request.form['expiryDate'], "%Y-%m-%d")
        entryTime = datetime.utcnow() + timedelta(hours=5, minutes=30)
        stock=Stock(itemCode=itemCode, itemName=itemName, stockSize=stockSize, expiryDate=expiryDate, entryTime=entryTime)
        db.session.add(stock)
        db.session.commit()
        flash('Stock added successfully')
        return redirect(url_for('inventory'))
        
    return render_template('stock.html')

@app.route('/')
@app.route('/inventory')
@login_required
def inventory():

    page = request.args.get('page', 1, int)   
    searchKeyword = request.args.get('search', 'all')
   
    if searchKeyword == 'all': 
        allStocks=Stock.query.order_by(desc(Stock.id)).paginate(page=page, per_page=ROWS_PER_PAGE)
    else:
        allStocks=Stock.query.filter(
            or_(
                Stock.itemCode.contains(searchKeyword),
                Stock.itemName.contains(searchKeyword)
        )).order_by(desc(Stock.id)).paginate(page=page, per_page=ROWS_PER_PAGE)
    
    return render_template('inventory.html', allStocks=allStocks, searchKeyword=searchKeyword)

@app.route('/reports')
@login_required
def reports():

    due=request.args.get('due', 1, int)
    page = request.args.get('page', 1, int)  
    searchKeyword = request.args.get('search', 'all')
    today=datetime.today()
    if due == 1:
        dueDate= today + relativedelta(months=+1)
    elif due == 3:
        dueDate= today + relativedelta(months=+3)
    elif due == 6:
        dueDate= today + relativedelta(months=+6)
    elif due == 12:
        dueDate= today + relativedelta(years=+1)
    
    if searchKeyword == 'all':
        stocks=Stock.query.filter(
            and_(
                Stock.expiryDate >= today,
                Stock.expiryDate <= dueDate
        )).order_by(Stock.expiryDate).paginate(page=page, per_page=ROWS_PER_PAGE)
    else:
        stocks=Stock.query.filter(
            and_(
                Stock.expiryDate >= today,
                Stock.expiryDate <= dueDate
        )).filter(
            or_(
                Stock.itemCode.contains(searchKeyword),
                Stock.itemName.contains(searchKeyword)
        )).order_by(Stock.expiryDate).paginate(page=page, per_page=ROWS_PER_PAGE)
     
    return render_template('reports.html', stocks=stocks, due=due, searchKeyword=searchKeyword)
    


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    stock= Stock.query.filter_by(id=id).first()
    db.session.delete(stock)
    db.session.commit() 
    flash('Stock deleted successfully')
    return redirect(url_for('inventory'))

@app.route('/update/<int:id>', methods= ['POST', 'GET'])
@login_required
def update(id):
    if request.method == 'GET':
        stock=Stock.query.filter_by(id=id).first()
        return render_template('update.html', stock=stock)
    elif request.method == 'POST':
        stock=Stock.query.filter_by(id=id).first()
        stock.itemCode = request.form['itemCode']
        stock.itemName = request.form['itemName']
        stock.stockSize = request.form['stockSize']
        stock.expiryDate = datetime.strptime(request.form['expiryDate'], "%Y-%m-%d")
        
        db.session.add(stock)
        db.session.commit()
        flash('Stock updated successfully')
        return redirect(url_for('inventory'))


# REST ENDPOINTS

@app.route('/user', methods=['POST'])
def create_user():
    try:
        username =  request.json['username']
        password = request.json['password']
        role_level=""
        if 'role_level' in request.json:
            role_level = request.json['role_level']
        user=User(username=username, password=password)
        if role_level != "":
            user.role_level=int(role_level)
        db.session.add(user)
        db.session.commit()
    except Exception as ex:
        return "{ \"message\":\"An exception was thrown\", \"detailedMessage\": \"" + str(ex) + "\" }", 500

    user=User.query.filter_by(username=username).first()

    return "{ \"message\":\"Created\",  \"data\":" + str(user) + "}", 201

@app.route('/user', methods=['PUT'])
def update_user():
    try:
        username =  request.json['username']
        password=""
        if 'password' in request.json:
            password = request.json['password']
        role_level=""
        if 'role_level' in request.json:
            role_level = request.json['role_level']
        user=User.query.filter_by(username=username).first()
        if user is None:
            new_user=User(username=username, password=password)
            if role_level != "":
                new_user.role_level=int(role_level)
            db.session.add(new_user)
            db.session.commit()
            return "{ \"message\":\"Created\",  \"data\":" + str(new_user) + "}", 201
        
        user.username=username
        if password != "":
            user.password=password
        if role_level != "":
            user.role_level=int(role_level)
        db.session.add(user)
        db.session.commit()
        return "{ \"message\":\"Updated\",  \"data\":" + str(user) + "}", 200
        
    except Exception as ex:
        return "{ \"message\":\"An exception was thrown\", \"detailedMessage\": \"" + str(ex) + "\" }", 500

@app.route('/user', methods=['GET'])
@app.route('/user/<string:username>', methods=['GET'])
def get_users(username=""):
    try:
        if username == "":
            return "{ \"message\":\"Success\",  \"data\":" + str(User.query.all()) + "}", 200
        else:
            user=  User.query.filter_by(username=username).first()
            user = user if user is not None else "[]"
            return "{ \"message\":\"Success\",  \"data\":" + str(user) + "}", 200      
    except Exception as ex:
        return "{ \"message\":\"An exception was thrown\", \"detailedMessage\": \"" + str(ex) + "\" }", 500

@app.route('/user/<string:username>', methods=['DELETE'])
def delete_user(username):
    try:
        user=User.query.filter_by(username=username).first()
        if user is not None:
            db.session.delete(user)
            db.session.commit()
            return "{ \"message\":\"Deleted\",  \"data\":" + str(user) + "}"
        else:
            return "{ \"message\":\"Not Found\", \"detailedMessage\":\"User does not exist\" }", 404
    except Exception as ex:
        return "{ \"message\":\"An exception was thrown\", \"detailedMessage\": \"" + str(ex) + "\" }", 500

    

if __name__ == '__main__':
    app.run(debug=False)
