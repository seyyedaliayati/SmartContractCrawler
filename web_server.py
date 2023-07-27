from flask import Flask, render_template

from db import get_web_data

app = Flask(__name__)


@app.route('/')
def index():
    data = []
    db_data = get_web_data()
    for item in db_data:
        data.append({
            'address': item[0],
            'name': item[1]
        })
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)