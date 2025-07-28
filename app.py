from flask import Flask, render_template, jsonify
from dune_client.client import DuneClient
from dune_client.types import QueryParameter
from dune_client.query import QueryBase
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from command line argument or environment variable
API_KEY = None
if len(sys.argv) > 1:
    API_KEY = sys.argv[1]
    print("Using API key from command line argument")
else:
    API_KEY = os.getenv("API_KEY")
    if API_KEY:
        print("Using API key from environment variable")

if not API_KEY:
    print("Error: API_KEY not provided!")
    print("Usage: python app.py <API_KEY>")
    print("   OR: Set API_KEY in .env file and run: python app.py")
    sys.exit(1)

app = Flask(__name__)

def get_dynamic_days():
    """
    Calculate days of data to fetch based on reference date 07/27/2025
    Every day after 07/27/2025, adds 1 to the base 150 days
    """
    reference_date = datetime(2025, 7, 27)
    current_date = datetime.now()
    
    if current_date.date() > reference_date.date():
        days_since_reference = (current_date.date() - reference_date.date()).days
    else:
        days_since_reference = 0
    
    base_days = 150
    dynamic_days = base_days + days_since_reference
    return dynamic_days

def fetch_dc_burn_data():
    """
    Fetch DC burned data from Dune Analytics with dynamic day calculation
    Automatically saves to dune_query_result.json
    """
    try:
        days = get_dynamic_days()
        print(f"Fetching {days} days of data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Initialize Dune Analytics client with API key
        dune = DuneClient(API_KEY)

        # Create parameterized query for DC burned data
        # Query ID 5543649 contains the SQL logic for fetching hourly DC burned data by OUI
        query = QueryBase(
            query_id=5543649,
            params=[
                QueryParameter.number_type(name="days", value=days)
            ]
        )

        # Execute the query and get results
        query_result = dune.run_query(query)

        # Extract data from Dune's response object
        # Different Dune client versions may structure results differently
        if hasattr(query_result, 'result'):
            result_obj = query_result.result
        elif hasattr(query_result, 'data'):
            result_obj = query_result.data
        else:
            raise ValueError("Cannot find serializable data in query_result.")

        # Get the actual rows of data for JSON serialization
        if hasattr(result_obj, 'rows'):
            serializable_data = result_obj.rows  # List of dictionaries with DC burned data
        elif hasattr(result_obj, 'data'):
            serializable_data = result_obj.data
        else:
            raise ValueError("Cannot find serializable data (e.g., .rows or .data) in result_obj.")

        # Save data to JSON file for Flask backend consumption
        with open("dune_query_result.json", "w") as f:
            json.dump(serializable_data, f, indent=2)

        print(f"Successfully fetched and saved {days} days of data to dune_query_result.json")
        return True

    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return False

def initialize_data():
    """
    Initialize data on startup if file doesn't exist or is older than 24 hours
    """
    json_path = "dune_query_result.json"
    should_fetch = False
    
    if not os.path.exists(json_path):
        print("No existing data file found. Fetching initial data...")
        should_fetch = True
    else:
        # Check if file is older than 24 hours
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(json_path))
        time_diff = datetime.now() - file_mod_time
        if time_diff.total_seconds() > 24 * 3600:  # 24 hours in seconds
            print("Existing data is older than 24 hours. Fetching fresh data...")
            should_fetch = True
        else:
            print(f"Using existing data from {file_mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if should_fetch:
        fetch_dc_burn_data()

@app.route('/')
def dashboard():
    """Serves the main forecasting dashboard interface"""
    return render_template('dashboard.html')

@app.route('/data')
def data():
    """API endpoint that provides historical DC burned data for forecasting"""
    try:
        json_path = os.path.join(app.root_path, 'dune_query_result.json')
        
        # Check if file exists, if not try to fetch data
        if not os.path.exists(json_path):
            print("Data file not found. Attempting to fetch data...")
            if fetch_dc_burn_data():
                # File should now exist
                pass
            else:
                return jsonify({"error": "Unable to fetch data"}), 500
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        return jsonify(data)
    
    except Exception as e:
        print(f"Error serving data: {str(e)}")
        return jsonify({"error": "Unable to load data"}), 500

@app.route('/status')
def status():
    """Status endpoint to check data freshness and next update time"""
    json_path = "dune_query_result.json"
    status_info = {
        "current_days": get_dynamic_days(),
        "reference_date": "2025-07-27",
        "current_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "api_key_source": "command_line" if len(sys.argv) > 1 else "environment"
    }
    
    if os.path.exists(json_path):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(json_path))
        status_info["last_update"] = file_mod_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate next update time (24 hours from last update)
        next_update = file_mod_time.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        status_info["next_update"] = next_update.strftime('%Y-%m-%d %H:%M:%S')
    else:
        status_info["last_update"] = "No data file found"
        status_info["next_update"] = "Immediate"
    
    return jsonify(status_info)

def setup_scheduler():
    """
    Setup background scheduler to fetch data every 24 hours at midnight
    """
    scheduler = BackgroundScheduler()
    
    # Schedule daily data fetch at midnight
    scheduler.add_job(
        func=fetch_dc_burn_data,
        trigger="cron",
        hour=0,
        minute=0,
        id='daily_data_fetch',
        name='Fetch DC burn data daily',
        replace_existing=True
    )
    
    scheduler.start()
    print("Background scheduler started. Data will be fetched daily at midnight.")
    return scheduler

if __name__ == '__main__':
    # Initialize data on startup
    print("Initializing DC Burn Forecasting System...")
    print(f"Reference date: 2025-07-27")
    print(f"Current dynamic days: {get_dynamic_days()}")
    
    # Initialize data if needed
    initialize_data()
    
    # Setup background scheduler for daily updates
    scheduler = setup_scheduler()
    
    try:
        # Start Flask development server with debug mode for auto-reloading
        print("Starting Flask server on http://localhost:5000")
        print("Dashboard: http://localhost:5000")
        print("Data API: http://localhost:5000/data")
        print("Status: http://localhost:5000/status")
        
        app.run(debug=True, use_reloader=False)  # use_reloader=False to prevent scheduler conflicts
        
    except KeyboardInterrupt:
        print("Shutting down...")
        scheduler.shutdown()
