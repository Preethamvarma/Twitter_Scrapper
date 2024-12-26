# Twitter Trends Scraper

This project scrapes trending topics from Twitter (now X) and stores them in a MongoDB database. It uses Selenium for web scraping, ProxyMesh for IP rotation, and Flask for a simple web interface. The scraper is designed to be robust, handling dynamic content loading, and storing results efficiently.

---

## Features

1. **Web Scraping**  
   - Extracts the top 5 trending topics from the "What’s Happening" section on X.  
   - Handles dynamic loading and login requirements.  

2. **Proxy Support**  
   - Integrates ProxyMesh to send requests from different IP addresses for each scraping session.  

3. **Data Storage**  
   - Stores results in a MongoDB database with the following fields:  
     - Unique ID for each scraping session.  
     - Names of 5 trending topics.  
     - Timestamp of scraping completion.  
     - IP address used for the query.  

4. **Web Interface**  
   - Simple HTML page powered by Flask, featuring:  
     - A button to trigger the scraper.  
     - Results displayed dynamically, including trends, IP address, and JSON output from MongoDB.  

---

## Setup Instructions

### **Prerequisites**  
1. Python 3.7+ installed on your system.  
2. MongoDB installed locally or a cloud instance configured.  
3. Chrome browser installed.  
4. ChromeDriver (automatically managed using `webdriver-manager`).  

---

### **Installation**  

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/Preethamvarma/Twitter_Scrapper.git
   cd Twitter_Scrapper
   ```

2. **Create a Virtual Environment**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # For Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**  
   - Create a `.env` file in the project root and define:  
     ```env
     MONGO_URI=mongodb://<username>:<password>@<host>:<port>/<database>
     TWITTER_USERNAME=<your_twitter_username>
     TWITTER_PASSWORD=<your_twitter_password>
     PROXY_HOST=<proxymesh_host>
     PROXY_PORT=<proxymesh_port>
     PROXY_USERNAME=<proxymesh_username>
     PROXY_PASSWORD=<proxymesh_password>
     ```

---

## Usage

### **Running the Scraper**

1. **Start MongoDB**  
   Ensure your MongoDB service is running locally or accessible through the configured URI.

2. **Start the Flask Application**  
   ```bash
   flask --app app run
   ```

3. **Access the Web Interface**  
   Open your browser and navigate to:  
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

4. **Trigger the Script**  
   - Click the button to scrape Twitter trends.  
   - View the top 5 trends, IP address used, and a JSON extract of the database record.  

---

## Project Structure

```plaintext
.
├── scrapper.py         # Core logic for scraping and data storage
├── app.py              # Flask application for the web interface
├── templates/
│   └── index.html      # HTML template for the web interface
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .env                # Environment variables (not committed to Git)
```

---

## Expected Output

### **Web Page View**  
```
These are the most happening topics as on {Date and Time of end of Selenium Script}:
- Name of trend1
- Name of trend2
- Name of trend3
- Name of trend4
- Name of trend5

The IP address used for this query was XXX.XXX.XXX.XXX.

Here’s a JSON extract of this record from the MongoDB:
[
    {
        "_id": { "$oid": "64b3cd15ab9c8b0013e91a9d" },
        "trend1": "Trend A",
        "trend2": "Trend B",
        "trend3": "Trend C",
        "trend4": "Trend D",
        "trend5": "Trend E",
        "datetime": "2024-12-26T12:00:00Z",
        "ip_address": "192.168.1.1"
    }
]
```

---

## Troubleshooting

1. **Proxy Issues**  
   - Ensure ProxyMesh credentials are correct.  
   - Verify network connectivity and the proxy configuration.

2. **Selenium Errors**  
   - Update ChromeDriver if browser versions mismatch.  
   - Adjust XPath or CSS selectors if Twitter changes its page structure.

3. **MongoDB Connection Errors**  
   - Verify the `MONGO_URI` in the `.env` file.  
   - Ensure the MongoDB service is running and accessible.  

4. **Login Challenges**  
   - Check Twitter credentials and handle CAPTCHA or 2FA manually if required.  

---
