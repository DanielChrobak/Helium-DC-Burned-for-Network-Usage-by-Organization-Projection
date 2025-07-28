from dune_client.client import DuneClient
from dune_client.types import QueryParameter
from dune_client.query import QueryBase
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is not set in .env file!")

# Get user input for number of days
while True:
    try:
        days = int(input("Enter the number of days of data you want to retrieve: "))
        if days > 0:
            break
        else:
            print("Please enter a positive number.")
    except ValueError:
        print("Please enter a valid number.")

print(f"Fetching {days} days of data...")

# Initialize Dune client
dune = DuneClient(API_KEY)

# Create query with parameters
query = QueryBase(
    query_id=5543649,
    params=[
        QueryParameter.number_type(name="days", value=days)
    ]
)

# Execute the query with parameters
query_result = dune.run_query(query)

# Extract the data from the result
if hasattr(query_result, 'result'):
    result_obj = query_result.result
elif hasattr(query_result, 'data'):
    result_obj = query_result.data
else:
    raise ValueError("Cannot find serializable data in query_result.")

# Now try to extract 'rows' from the result object
if hasattr(result_obj, 'rows'):
    serializable_data = result_obj.rows  # This should be a list of dicts
elif hasattr(result_obj, 'data'):
    serializable_data = result_obj.data
else:
    raise ValueError("Cannot find serializable data (e.g., .rows or .data) in result_obj.")

# Save to JSON file
with open("dune_query_result.json", "w") as f:
    json.dump(serializable_data, f, indent=2)

print(f"Results for {days} days written to dune_query_result.json")
