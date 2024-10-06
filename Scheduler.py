import os
import datetime
import holidays  # Make sure to install the holidays package
import logging

# Set up logging
logging.basicConfig(filename="./ScheduleLogger.log", level=logging.INFO)

#################################################################################################################################################################
# Function: is_market_open
# Parameters: N/A
# is_market_open checks if the day is a weekday and not a US holiday
#
#
# output:
#################################################################################################################################################################
def is_market_open():
    us_holidays = holidays.US()
    today = datetime.date.today()
    if today.weekday() < 5 and today not in us_holidays: #monday starts at 0
        return True
    return False

if __name__ == "__main__":
    logging.info("Script started at: " + str(datetime.datetime.now()))
    if is_market_open():
        logging.info("Market is open. Running ScheduledScraping.py")
        os.system("python C:\\Users\\Josh\\Desktop\\Winter2024\\ScheduledScraping.py")
        #os.system("python ./Stockmodel.py")
    else:
        logging.info("Market is closed. Script will not run.")
    logging.info("Script finished at: " + str(datetime.datetime.now()))
