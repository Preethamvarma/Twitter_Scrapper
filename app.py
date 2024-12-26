from flask import Flask, render_template, jsonify, g
from pymongo import MongoClient
from scrapper import scrape_twitter, get_chromedriver_path, create_chrome_driver
import os
from datetime import datetime
import socket
from flask import request
import threading
import scrapper
import logging

# Initialize Flask app
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['MONGO_URI'] = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")  # Default to localhost if not set
app.config['DB_NAME'] = "twitter_scraper"
app.config['COLLECTION_NAME'] = "trending_topics"

# Thread lock for synchronization
lock = threading.Lock()

def get_db():
    """Get the MongoDB client connection."""
    if 'db' not in g:
        g.db = MongoClient(app.config['MONGO_URI'])[app.config['DB_NAME']][app.config['COLLECTION_NAME']]
    return g.db

def close_db(e=None):
    """Close the MongoDB connection."""
    db = g.pop('db', None)
    if db is not None and hasattr(db, 'client'):
        db.client.close()



@app.teardown_appcontext
def teardown_db(error):
    """Teardown function to close the database connection."""
    close_db(error)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run_script', methods=['GET'])
def run_script():
    with lock:
        driver = None
        try:
            driver = scrapper.create_chrome_driver() # Proxy setup is handled in scrapper.py
            if driver:
                result = scrapper.scrape_twitter(driver)
                if result:
                    ip_address = request.remote_addr
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    formatted_result = {
                        "trends": result.get("trends", []),  # Use .get() for safety
                        "timestamp": timestamp,
                        "ip_address": ip_address,
                        "mongo_record": result
                    }
                    return jsonify(formatted_result), 200
                else:
                    return jsonify({"error": "Scraping failed. Check scrapper.py logs."}), 500  # More specific error message
            else:
                return jsonify({"error": "Failed to create ChromeDriver."}), 500
        except Exception as e:
            app.logger.error(f"Error in run_script: {e}")  # Log the error
            return jsonify({"error": str(e)}), 500  # Return a generic error response
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    app.run(debug=True)
