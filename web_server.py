import json

from collections import OrderedDict

from flask import Flask, render_template

from db import get_web_data, get_details_for_address, get_count_all

app = Flask(__name__)

@app.route('/api/address/<address>')
def address_details(address):
    details = get_details_for_address(address)
    if details is None:
        return {
            'error': 'Address not found'
        }, 404
    else:
        details['ABI'] = json.loads(details['ABI'])
        
    return {
        'address': address,
        'details': details
    }

@app.route('/')
def index():
    data = []
    db_data = get_web_data(limit=10000)
    all_count = get_count_all()
    
    for item in db_data:
        details = get_details_for_address(item[0])
        data.append({
            'address': item[0],
            'name': item[1],
            'details': details,
            'all_count': all_count
        })
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)