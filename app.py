from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    """Serves the main forecasting dashboard interface"""
    return render_template('dashboard.html')

@app.route('/data')
def data():
    """API endpoint that provides historical DC burned data for forecasting"""
    # Load data from JSON file in the application directory
    json_path = os.path.join(app.root_path, 'dune_query_result.json')
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    return jsonify(data)

if __name__ == '__main__':
    # Start development server with debug mode for auto-reloading
    app.run(debug=True)
