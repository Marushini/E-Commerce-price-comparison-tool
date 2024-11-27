from flask import Flask, request, render_template
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Initialize the Flask app
app = Flask(__name__)

# Function to initialize the Selenium WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    # Add any specific options you need
    driver_path = ChromeDriverManager().install()  # Automatically download the appropriate driver
    service = Service(driver_path)  # Use Service instead of executable_path
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Scraper function for Amazon
def get_amazon_price(product_name):
    driver = init_driver()
    url = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}"
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = []
    
    for item in soup.select(".s-result-item"):
        title = item.select_one("h2 .a-link-normal").get_text(strip=True) if item.select_one("h2 .a-link-normal") else "N/A"
        price = item.select_one(".a-price .a-offscreen").get_text(strip=True) if item.select_one(".a-price .a-offscreen") else "N/A"
        availability = "In Stock" if item.select_one(".s-title-instructions-style") else "Out of Stock"
        results.append({"site": "Amazon", "title": title, "price": price, "availability": availability})

    driver.quit()
    return results

# Scraper function for eBay
def get_ebay_price(product_name):
    driver = init_driver()
    url = f"https://www.ebay.com/sch/i.html?_nkw={product_name.replace(' ', '+')}"
    driver.get(url)
    time.sleep(3)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = []
    
    for item in soup.select(".s-item"):
        title = item.select_one(".s-item__title").get_text(strip=True) if item.select_one(".s-item__title") else "N/A"
        price = item.select_one(".s-item__price").get_text(strip=True) if item.select_one(".s-item__price") else "N/A"
        availability = "Available"
        results.append({"site": "eBay", "title": title, "price": price, "availability": availability})

    driver.quit()
    return results

# Main function to aggregate price data from Amazon and eBay
def scrape_prices(product_name):
    amazon_data = get_amazon_price(product_name)
    ebay_data = get_ebay_price(product_name)
    all_data = amazon_data + ebay_data
    return pd.DataFrame(all_data)

# Flask route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    if request.method == "POST":
        product_name = request.form.get("product")
        data = scrape_prices(product_name)
        data = data.to_dict(orient="records")
    return render_template("index.html", data=data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
