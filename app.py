from operator import or_
from flask import Flask, render_template, request, redirect, flash
from datetime import datetime
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# DB Models

class Stock(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    itemCode=db.Column(db.String(30), nullable=False)
    itemName=db.Column(db.String(80), nullable=False)
    stockSize=db.Column(db.Integer, nullable=False)
    entryTime=db.Column(db.DateTime, default=datetime.utcnow())
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

        stock=Stock(itemCode=itemCode, itemName=itemName, stockSize=stockSize, expiryDate=expiryDate)
        db.session.add(stock)
        db.session.commit()
        flash('Stock added successfully')
        return redirect(url_for('inventory'))
        
    return render_template('stock.html')

@app.route('/inventory')
def inventory():
    ROWS_PER_PAGE=10
    page = request.args.get('page', 1, int)   
    searchKeyword = request.args.get('search', 'all')
    print(searchKeyword)
    if searchKeyword == 'all': 
        allStocks=Stock.query.order_by(desc(Stock.id)).paginate(page=page, per_page=ROWS_PER_PAGE)
    else:
        allStocks=Stock.query.filter(
            or_(
                Stock.itemCode.contains(searchKeyword),
                Stock.itemName.contains(searchKeyword)
        )).order_by(desc(Stock.id)).paginate(page=page, per_page=ROWS_PER_PAGE)
    
    return render_template('inventory.html', allStocks=allStocks)

@app.route('/reports')
def reports():
    return render_template('reports.html')

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
