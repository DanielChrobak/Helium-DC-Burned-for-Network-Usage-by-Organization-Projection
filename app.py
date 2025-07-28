from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/data')
def data():
    json_path = os.path.join(app.root_path, 'dune_query_result.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
