from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from getpass import getpass
import time
import uuid
import requests
import datetime
import os
from pymongo import MongoClient
import logging

# Retrieve environment variables
PROXY_USERNAME = "Preetham"  # Replace with your actual username
PROXY_PASSWORD = "***"
PROXY_HOST = "p.webshare.io"
PROXY_PORT = "9999"
MONGO_URI = "mongodb://localhost:27017/"
TWITTER_USERNAME = "PreethamVarma11"
# Configure MongoDB
DB_NAME = "twitter_scraper"
COLLECTION_NAME = "trending_topics"


def get_chromedriver_path():
    """Tries to find chromedriver executable in common locations."""
    locations = [
        r"C:\Users\preet\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe",  # Original location
        "/usr/local/bin/chromedriver",  # Common Linux/macOS location
        "/usr/bin/chromedriver",  # Another possible location
        "./chromedriver",  # Current directory (less common)
    ]
    for location in locations:
        if os.path.exists(location):
            return location
    return None  # Return None if chromedriver is not found


def create_chrome_driver():
    try:
        chrome_options = Options()
         # Proxy configuration (without authentication)
        if PROXY_HOST and PROXY_PORT:
            proxy_string = f"http://{PROXY_HOST}:{PROXY_PORT}"  # No username/password!
            chrome_options.add_argument(f'--proxy-server={proxy_string}')
            print(f"Using proxy (IP auth): {proxy_string}")
        else:
            logging.warning("Proxy not configured. Running without proxy.")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logging.info("ChromeDriver created successfully.")
        return driver
    except Exception as e:
        logging.exception(f"Error creating ChromeDriver: {e}")  # Log exception for traceback
        return None


def send_keys_and_enter(element, text):
    element.send_keys(text)
    element.send_keys(Keys.RETURN)


def scrape_twitter(driver):
    wait = WebDriverWait(driver, 120)
    unique_id = str(uuid.uuid4())
    try:
        driver.get("https://x.com/i/flow/login")
        logging.info("Navigated to X login page.")

        # 1. Username entry:
        username_input = wait.until(EC.element_to_be_clickable((By.NAME, "text")))
        username_input.send_keys(TWITTER_USERNAME)
        username_input.send_keys(Keys.RETURN)
        logging.info(f"Entered username: {TWITTER_USERNAME}")

        # 2. Handle potential challenge page (phone/email verification):
        try:
            challenge_locator = (By.XPATH, "//*[contains(text(),'We sent you a code')] | //*[contains(text(),'Enter your phone number or email address')] | //*[contains(text(), 'Enter your email address or username')]")
            challenge_element = wait.until(EC.presence_of_element_located(challenge_locator))
            logging.info("Challenge detected. Please handle the challenge manually.")

            # Wait for user to handle the challenge and press Enter to continue:
            input("Press Enter after handling the challenge in the browser...")
            logging.info("Challenge appears to be handled.")

        except Exception as challenge_error:
            logging.info(f"No challenge detected or challenge handling timed out: {challenge_error}")

        # 3. Password entry (Manual):
        try:
            wait.until(EC.presence_of_element_located((By.NAME, "password")))
            logging.info("Password field detected.  Entering password manually...")

            input("Please enter your password in the browser and press Enter to continue...")
            logging.info("Password appears to be entered.")

            # Verify login (after manual password entry):
            wait.until(EC.url_to_be("https://x.com/home")) # Check for URL change after login.
            logging.info("Login appears successful.")

        except Exception as password_error:
            logging.exception(f"Password entry or login verification failed: {password_error}")
            return None
        # 3. Post-login verification and scraping
        try:
            print("Verifying login and waiting for home link...") # Check element that appears after log in
            wait.until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Home']"))) # Example check, you'll likely need to adjust this.


            print("Login successful. Scraping trends...")
            wait = WebDriverWait(driver, 120)

            top_trends = []
    # Approach 1: Using data-testid (Most Recommended)
            try:
                trends_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='trend']")))

                for trend_element in trends_elements:
                    trend_name_element = trend_element.find_element(By.XPATH, "./div[2]/span") # Direct path to the name within trend element
                    top_trends.append(trend_name_element.text)
                    if len(top_trends) == 4:  # Click show more *only* when 4 trends are found
                        try:
                            show_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='trend']/ancestor::div[1]//a[contains(text(), 'Show more')]")))
                            show_more_button.click()
                            time.sleep(3)  # Adjust as needed
                            # Get the 5th trend *after* clicking "Show more":
                            fifth_trend_element = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@data-testid='trend'])[5]/div[2]/span")))  # Use correct indexing
                            top_trends.append(fifth_trend_element.text)

                        except Exception as e:
                            print(f"Error clicking 'Show more' or finding 5th trend: {e}")
                            # Log, handle error gracefully (or try another approach). Note that if you want another approach to be executed if show more button or 5th element is not loaded, remove break and keep the approach in try..except block and handle its exceptions, so that any of those approaches would provide desired result if others fail to load webpage completely.
                            break
            except: #Try another approach if approach one fails
                print("Approach 1 failed. Trying approach 2...")
                # Approach 2: Refined XPath with Class Name and Text Content
                try:

                    trends_elements = wait.until(EC.presence_of_all_elements_located(
                        (By.XPATH, "//span[contains(@class,'r-bcqeeo') and contains(@class, 'r-qvutc0') and contains(text(), '#')]")
                    ))

                    top_trends = [trend.text for trend in trends_elements[:5]]


                except:
                    print("Approach 2 failed. Trying approach 3...")
                    # Approach 3: Explicit wait for each trend (Handles dynamic loading)
                    for i in range(5):
                        try:
                            trend_locator = (By.XPATH, f"(//div[@data-testid='trend'])[{i+1}]//span[contains(@class, 'r-poiln3')]")
                            trend_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(trend_locator))
                            top_trends.append(trend_element.text)
                        except:
                            print(f"Trend {i+1} not found. Stopping.")
                            break  # Stop if a trend isn't found within the timeout



            if len(top_trends) < 5:
                print(f"Warning: Only {len(top_trends)} trends scraped!")


            end_time = datetime.datetime.now()


            try:
                # Get IP address within the browser context:
                driver.get("http://api.ipify.org")  # Navigate to ipify.org *using* the proxy configured in the driver
                wait = WebDriverWait(driver, 120) # Ensure there is wait
                ip_address = wait.until(EC.presence_of_element_located((By.TAG_NAME, "pre"))).text
                print(f"Retrieved IP (via Selenium): {ip_address}") # Verify IP

            except requests.exceptions.RequestException as ip_error:
                print(f"IP retrieval error: {ip_error}")
                ip_address = "Unknown"   # Use a more descriptive error value



            # Save to MongoDB
            client = MongoClient(MONGO_URI)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]

            record = {
                "_id": unique_id,
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "ip_address": ip_address,
                **{f"trend{i}": trend for i, trend in enumerate(top_trends, start=1)} # Include trends directly
            }

            collection.insert_one(record)
            print(f"Record inserted into MongoDB: {record}")
            return record  # Return the scraped record

        except Exception as scraping_error:
            print(f"Scraping error: {scraping_error}")
            return None

    except Exception as e:
        print(f"Overall error in scrape_twitter: {e}")
        return None  # Always return None on error


if __name__ == "__main__":
    print("Starting scraper...")
    driver = create_chrome_driver()
    if driver:
        result = scrape_twitter(driver)
        if result:
            print("Scraped data:", result)
        driver.quit()
