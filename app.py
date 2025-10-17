from flask import Flask, render_template
import json

app = Flask(__name__)

def get_economic_data():
    with open('data.json', 'r') as f:
        data = json.load(f)
    return data

@app.route('/')
def index():
    economic_data = get_economic_data()
    return render_template('index.html', events=economic_data)

if __name__ == "__main__":
    app.run(debug=True)