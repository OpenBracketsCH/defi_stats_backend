from flask import Flask, jsonify
from github import Github
import json
import sqlite3
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
import os
import requests


g_token = os.getenv("GITHUB_TOKEN")

g = Github(g_token)
repo = g.get_repo("OpenBracketsCH/defi_data")

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)
# Scheduler for daily fetch at 12:00 PM
scheduler = BackgroundScheduler(timezone="CET")
scheduler.add_job(func=lambda: fetch_defi(), trigger="cron", minute='00')
scheduler.start()

@app.route('/')
def hello_world():
    return 'Welcome to the DeFi Data API!\n FLASK_ENV is set to: {os.environ.get("FLASK_ENV")}'

def fetch_geojson_data():
    """Fetches the geojson data from the GitHub repository."""
    try:
        file_content = repo.get_contents("data/json/defis_switzerland.geojson", ref="main")
        print(file_content)
        response = requests.get(file_content.download_url)
        response.raise_for_status()  
        decoded_content = response.json()
        return decoded_content
    except Exception as e:
        print(f"Error fetching geojson data: {e}")
        return None

def fetch_defi():
    """Fetches DeFi data and stores it in the SQLite database."""
    data = fetch_geojson_data()
    if data is None:
        return
    
    all_defi = find_defi(data["features"], "Feature")
    today = datetime.today().strftime('%Y-%m-%d')

    with sqlite3.connect('defi_data.db') as con:
        cur = con.cursor()
        cur.execute("INSERT INTO defi_data (value,time) VALUES (?, ?)", (all_defi, today))
        con.commit()

def find_defi(json_obj, name):
    """Counts the number of DeFi entries in the geojson data."""
    return sum(1 for entry in json_obj if entry['type'] == name)

def piechart_data():
    """Generates pie chart data from geojson file."""
    data = fetch_geojson_data()
    if data is None:
        return {}

    json_obj = data["features"]
    pie_data = {
        "all": len(json_obj),
        "unknown": sum(1 for entry in json_obj if "opening_hours" not in entry["properties"]),
        "open_only": sum(1 for entry in json_obj if "opening_hours" in entry["properties"]),
        "open_24": sum(1 for entry in json_obj if entry["properties"].get("opening_hours") == "24/7")
    }
    return pie_data

def barchart_data():
    """Generates bar chart data from geojson files containing 'defis_kt'."""
    with open('match.json', encoding="utf8") as f:
        match_data = json.load(f)

    contents = repo.get_contents("data/json")
    bar_data = {
        "label": [],
        "data": []
    }

    for content_file in contents:
        if 'defis_kt' in content_file.name:
            try:
                file_content = repo.get_contents(content_file.path)
                response = requests.get(file_content.download_url)
                response.raise_for_status()  # Raise an error for bad responses
                data = response.json()
                each_defi = find_defi(data["features"], "Feature")
                match_name = content_file.name.replace("defis_kt_", "").replace(".geojson", "")
                bar_data["label"].append(match_data.get(match_name, match_name))
                bar_data["data"].append(each_defi)
            except Exception as e:
                print(f"Error processing file {content_file.name}: {e}")

    return bar_data

def linechart_data():
    """Generates line chart data from the SQLite database."""
    result = {"label": [], "data": []}
    
    with sqlite3.connect('defi_data.db') as con:
        cur = con.cursor()
        cur.execute("""
            SELECT * FROM (
                SELECT * FROM defi_data GROUP BY time ORDER BY id DESC LIMIT 7
            ) Var1
            ORDER BY id ASC;
        """)
        rows = cur.fetchall()
        for row in rows:
            result["label"].append(row[2])  # Date
            result["data"].append(row[1])    # Value

    return result

def find_dispo():
    """Counts the number of files with 'dispo' in their names."""
    contents = repo.get_contents("data/json")
    return sum(1 for content_file in contents if 'dispo' in content_file.name)

@app.route('/api', methods=['GET'])
def fetch_json():
    try:
        """Fetches and returns combined data from various sources."""
        result_data = {}
        data = fetch_geojson_data()
        if data is None:
            return jsonify({"error": "Could not fetch data"}), 500

        all_defi = find_defi(data["features"], "Feature")
        all_hours = find_hours(data["features"], "24/7")
        dispo_data = find_dispo()

        result_data["all"] = all_defi
        result_data["hours"] = all_hours
        result_data["dispo"] = dispo_data
        result_data["bar_data"] = barchart_data()
        result_data["pie_data"] = piechart_data()
        result_data["line_data"] = linechart_data()

        return jsonify(result_data)
    except Exception as e:
        print(f"Error : {e}")
        return jsonify([])

def find_hours(json_obj, name):
    """Counts the number of DeFi entries with specified opening hours."""
    return sum(1 for entry in json_obj if entry.get("properties", {}).get("opening_hours") == name)

@app.errorhandler(Exception)
def handle_exception(e):
    # log the error
    print(f"Error: {e}")
    return jsonify(error=str(e)), 500

def getApp():
    """Returns the Flask app instance."""
    return app