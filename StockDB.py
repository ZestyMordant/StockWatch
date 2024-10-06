from StockWebScraper import webScrapper
import sqlite3
from datetime import datetime
import time




def connect(path):
    

    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute(' PRAGMA foreign_keys=ON; ')
        connection.commit()
        print("Connected to the database.")
        return connection, cursor
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None, None


def insert_stock(cursor, ticker, name, url):
    cursor.execute('''INSERT OR IGNORE INTO stocks (ticker, name, url) VALUES (?, ?, ?)''', (ticker, name, url))
    cursor.connection.commit()

def insert_tracking(cursor, stock_id, tracking, interval, percent_change):
    cursor.execute('''INSERT OR IGNORE INTO stock_tracking (stock_id, tracking, interval, percent_change_threshold) VALUES (?, ?, ?, ?)''', (stock_id, tracking, interval, percent_change))
    cursor.connection.commit()

def update_tracking(cursor, stock_id, tracking, interval, percent_change):
    cursor.execute(''' UPDATE stock_tracking SET tracking = ?, interval = ?, percent_change_threshold = ? WHERE stock_id = ?;  ''',(tracking,interval,percent_change,stock_id))
    cursor.connection.commit()

def insert_price_update(cursor, ticker, price):
    timestamp_now = datetime.now()
    cursor.execute('''INSERT INTO prices (stock_id, price, timestamp)
                      VALUES ((SELECT id FROM stocks WHERE ticker = ?), ?, ?)''',
                   (ticker, price, timestamp_now))
    cursor.connection.commit()

def insert_inter_day_price_update(cursor, stock_id, open, close, high, low, date, volume):
    insert_inter_day = '''INSERT INTO inter_day_prices (stock_id, open, close, high, low, date, volume) VALUES (?,?,?,?,?,?,?)'''
    cursor.execute(insert_inter_day,(stock_id, open, close, high, low, date, volume))
    cursor.connection.commit()
    
def insert_intra_day_price_update(cursor,stock_id ,price):
    timestamp_now = datetime.now()
    insert_intra_day='''INSERT INTO intra_day_prices (stock_id, price, timestamp) VALUES(?, ?, ?)'''
    cursor.execute(insert_intra_day,(stock_id ,price, timestamp_now))
    cursor.connection.commit()

#def drop_tables(cursor):
    
#    drop_stocks = "DROP TABLE IF EXISTS stocks"
#    drop_prices = "DROP TABLE IF EXISTS prices"
#    cursor.execute(drop_prices)
#    cursor.execute(drop_stocks)
    


def define_tables(cursor):
    
    stock_table = '''CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL
    );'''

    intra_day_price_table = '''CREATE TABLE IF NOT EXISTS intra_day_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL,
        price REAL NOT NULL,
        timestamp DATETIME NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id)
    );'''
    

    inter_day_prices_table = '''CREATE TABLE IF NOT EXISTS inter_day_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL,
        open REAL NOT NULL,
        close REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        date DATE NOT NULL,
        volume INTEGER NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id)
    );'''

    weekly_price_table = '''CREATE TABLE IF NOT EXISTS weekly_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL,
        open REAL NOT NULL,
        close REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        week_start DATE NOT NULL,
        week_end DATE NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id)
    );'''
    monthly_price_table='''CREATE TABLE IF NOT EXISTS monthly_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL,
        open REAL NOT NULL,
        close REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        month_start DATE NOT NULL,
        month_end DATE NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id)
    );'''
    yearly_price_table = '''CREATE TABLE IF NOT EXISTS yearly_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL,
        open REAL NOT NULL,
        close REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        year_start DATE NOT NULL,
        year_end DATE NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id)
    );'''
    transaction_table = '''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,  -- 'buy' or 'sell'
        quantity INTEGER NOT NULL,
        price REAL NOT NULL,
        transaction_date DATETIME NOT NULL,
        FOREIGN KEY (stock_id) REFERENCES stocks(id)
    )
    '''
    stock_tracking='''
    CREATE TABLE IF NOT EXISTS stock_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    tracking BOOLEAN NOT NULL DEFAULT 0,
    interval TEXT,
    percent_change_threshold REAL,
    FOREIGN KEY (stock_id) REFERENCES stocks(id)
    )
    '''

    cursor.execute(stock_table)
    cursor.execute(intra_day_price_table)
    cursor.execute(inter_day_prices_table)
    cursor.execute(weekly_price_table)
    cursor.execute(monthly_price_table)
    cursor.execute(yearly_price_table)
    cursor.execute(transaction_table)
    cursor.execute(stock_tracking)

    # Create indexes on stock_id to improve query performance
    #cursor.execute('''CREATE INDEX IF NOT EXISTS idx_stock_id ON prices(stock_id);''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_intra_day_stock_id ON intra_day_prices(stock_id);''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_inter_day_stock_id ON inter_day_prices(stock_id);''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_weekly_stock_id ON weekly_prices(stock_id);''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_monthly_stock_id ON monthly_prices(stock_id);''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_yearly_stock_id ON yearly_prices(stock_id);''')


    
    
    cursor.connection.commit()
    

def main():
    
    path = "./stockdb.db"

    connection, cursor = connect(path)    
    #drop_tables(cursor)
    define_tables(cursor)
    #insert_stock(cursor, 'CLSK', 'CleanSpark, Inc.','https://finance.yahoo.com/quote/CLSK/')
    #insert_stock(cursor,'BTC','Bitcoin','https://finance.yahoo.com/quote/BTC-USD/')
    

    connection.commit()
    connection.close()
    
    

if __name__ == "__main__":
    main()
