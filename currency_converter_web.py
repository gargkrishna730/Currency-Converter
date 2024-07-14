from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
API_KEY = "4fb1a521132a87a158434378"

def get_exchange_rate(from_currency, to_currency):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'][to_currency]
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_currency():
    from_currency = request.form['from_currency']
    to_currency = request.form['to_currency']
    amount = request.form['amount']
    
    if not amount:
        return jsonify({'error': 'Amount Not Entered. Please enter a valid amount.'})
    
    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid amount. Please enter a number.'})

    try:
        exchange_rate = get_exchange_rate(from_currency, to_currency)
        if exchange_rate:
            new_amount = exchange_rate * amount
            return jsonify({'result': round(new_amount, 4)})
        else:
            return jsonify({'error': 'Failed to fetch exchange rate. Please try again later.'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)