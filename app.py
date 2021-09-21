from enum import unique
from flask import Flask, render_template, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

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
        return self.itemCode + " " + self.itemName + " of quantity " + self.stockSize + " expires on " + self.expiryDate 

# Routes

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/stock', methods= ['POST', 'GET'])
def stock_pile():
    if request.method == 'POST':
        itemCode=request.form['itemCode']
        itemName=request.form['itemName']
        stockSize=request.form['stockSize']
        expiryDate=datetime.strptime(request.form['expiryDate'], "%Y-%m-%d")

        stock=Stock(itemCode=itemCode, itemName=itemName, stockSize=stockSize, expiryDate=expiryDate)
        db.session.add(stock)
        db.session.commit()
        return "<script>alert('Stock added successfully'); window.location.href = '/stock';</script>"
    return render_template('stock.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True)
