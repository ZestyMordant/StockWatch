from StockWebScraper import webScrapper
from NotifyUser import send_email
from StockDB import insert_intra_day_price_update,insert_stock,insert_tracking,update_tracking
from StockWatch import get_url,get_stock_id,get_average_price,get_interval,get_open_price,get_tickers,get_percent_change_threshold
import schedule
import datetime
import time
import sqlite3
import logging

logging.basicConfig(filename="C:\\Users\\Josh\\Desktop\\Winter2024\\ScrapingLog.log", level=logging.INFO)
#################################################################################################################################################################
# Function: update_db
# Parameters: N/A
# update_db just connects to the database in order to receive updates from the scraper
#
# output: connection, cursor
#################################################################################################################################################################
def update_db():
    try:
        connection = sqlite3.connect("C:\\Users\\Josh\\Desktop\\Winter2024\\stockdb.db")
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON;')
        connection.commit()
        print("Connected to the database.")
        return connection, cursor
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None, None
#################################################################################################################################################################
# Function: scrape_and_update
# Parameters:ticker, url, stock_id, cursor
# scrape_and_update scrapes the price of the ticker and writes to the database. It also sends an email to notify the user of a price change or just by interval depending on user preference
# 
# output: N/A
#################################################################################################################################################################
def scrape_and_update(ticker, url, stock_id, cursor):
    try:
        print(url)
        price = webScrapper(url)
        price = float(price)
        insert_intra_day_price_update(cursor, stock_id, price)
        
        # Optionally: Check average price and send email if needed
        average_price = get_average_price(cursor, ticker)
        open_price = get_open_price(cursor,ticker)
        percent_change_threshold = get_percent_change_threshold(cursor,ticker)
        percent_change_open = ((price - open_price)/open_price) * 100
        percent_change_average = ((price - average_price)/average_price) * 100
        logging.info(f"Scraped at: {str(datetime.datetime.now())}, Percent change from open: {percent_change_open}, Percent change from Average: {percent_change_average}, Average price: {average_price}")
        if percent_change_threshold:
            if(percent_change_threshold <= percent_change_open): #if the percent from open is greater than or equal to the percentage change threshold notify user
                send_email(f"Status update for {ticker}",f"Percent change from open {percent_change_open} Percent change from average price {percent_change_average}","kammerma@ualberta.ca")
        else:#percent change threshold doesnt exist so just go by interval
            send_email(f"Status update for {ticker}",f"Percent change from open {percent_change_open} Percent change from average price {percent_change_average}","kammerma@ualberta.ca")
        
        #add info to the select a ticker window 
        

    except Exception as e:
        print(f"Error scraping or updating for {ticker}: {e}")
#################################################################################################################################################################
# Function: schedule_jobs
# Parameters: cursor
# schedule_jobs schedules web scraping for each ticker that has notification settings enabled
#
# Output: N/A
#################################################################################################################################################################
def schedule_jobs(cursor):
    ticker_list = get_tickers(cursor)
    for ticker in ticker_list:
        url = get_url(cursor, ticker)
        stock_id = get_stock_id(cursor, ticker)
        interval = get_interval(cursor, ticker)
        if interval:
            if interval == '30 min ':
                time_interval = 30
            elif interval == '1 hour':
                time_interval = 60
            else:
                time_interval = 120
        
            # Schedule the job 
            schedule.every(time_interval).minutes.do(scrape_and_update, ticker=ticker, url=url, stock_id=stock_id, cursor=cursor)
            print(f"Scheduled scraping for {ticker} every {time_interval} minutes.")
        else:
            print(f"No interval found for {ticker}. Skipping scheduling.")
#################################################################################################################################################################
# Function: main 
# Parameters: N/A
# the main function runs a continuous loop until 2pm that will run a scheduled job program to routinely scrape prices of selected tickers. Interval is based off 
# tickers intervals from the database
# Output: N/A
#################################################################################################################################################################
def main():
    connection, cursor = update_db()
    schedule_jobs(cursor)

    # Main loop to keep the script running and execute scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)
        current_time = datetime.datetime.now().time()
        if current_time.hour == 14 and current_time.minute == 0:  # 2:00 PM
            connection.close()
            break


if __name__ == "__main__":
    main()



