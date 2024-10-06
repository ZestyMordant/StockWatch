from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from NotifyUser import send_email
import time
#################################################################################################################################################################
# Function: webScrapper
# Parameters: url
# webScrapper uses chrome Web driver and the Beautiful soup module to webscrape off yahoo finance to update the database
#
# output: price.text
#################################################################################################################################################################
def webScrapper(url):
    try: 
        chrome_options = Options()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')

        service = Service('C:\\Users\\Josh\\Desktop\\Winter2024\\chromedriver-win32\\chromedriver.exe')

        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to the URL
        driver.get(url)

        # Allow time for the JavaScript to execute and content to load
        time.sleep(5)

        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        live_prices = soup.find('div', class_='container yf-mgkamr')

        price = live_prices.find('fin-streamer',class_='livePrice yf-mgkamr')

        # Print the results
        #current_price = live_prices[0]
        #for price in live_prices:
        #    print(price.text)
        # Close the browser
        driver.quit()
        #print(price.text)
        if price is not None:
            return price.text
        else:
            raise ValueError("Price not found on the page")
        
    except Exception as e:
        send_email(f"Error scraping web",f"Error: {e}","kammerma@ualberta.ca")
        return None


    


