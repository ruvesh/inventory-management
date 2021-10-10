from operator import or_, and_
from time import timezone
from flask import Flask, render_template, request, redirect, flash
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy.sql.expression import case


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
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

# Routes

@app.route('/')
def home_page():

    return render_template('index.html')

@app.route('/stock', methods= ['POST', 'GET'])
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

@app.route('/inventory')
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
def delete(id):
    stock= Stock.query.filter_by(id=id).first()
    db.session.delete(stock)
    db.session.commit() 
    flash('Stock deleted successfully')
    return redirect(url_for('inventory'))

@app.route('/update/<int:id>', methods= ['POST', 'GET'])
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


if __name__ == '__main__':
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.run(debug=True)
