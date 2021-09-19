from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/stock')
def stock_pile():
    return render_template('stock.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    app.run(debug=True)
