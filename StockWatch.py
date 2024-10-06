from StockWebScraper import webScrapper
from NotifyUser import send_email
from StockDB import insert_inter_day_price_update,insert_stock,insert_tracking,update_tracking
import sqlite3
from datetime import datetime
import webbrowser
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import mplcursors
import matplotlib.pyplot as plt

api_key = "0WAM9DRZC9MOXP74Y"

#################################################################################################################################################################
# Function: db_connect
# Parameters: path
# db_connect connects the program to the database
#
# output: connection , cursor
#################################################################################################################################################################
def db_connect(path):
    try:
        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON;')
        connection.commit()
        print("Connected to the database.")
        return connection, cursor
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None, None  
    
#################################################################################################################################################################
# Function: insert_price_update
# Parameters:
#
#
# output:
#################################################################################################################################################################
def insert_price_update(cursor, ticker, price):
    timestamp_now = datetime.now()
    cursor.execute('''INSERT INTO prices (stock_id, price, timestamp)
                      VALUES ((SELECT id FROM stocks WHERE ticker = ?), ?, ?)''',
                   (ticker, price, timestamp_now))
    cursor.connection.commit()

#################################################################################################################################################################
# Function: get_prices
# Parameters:
#
#
# output:
#################################################################################################################################################################
def get_prices(cursor,selected_ticker):
    stock_id = get_stock_id(selected_ticker)
    price_list_query = '''SELECT price FROM prices WHERE stock_id = ? ORDER BY ASC'''
    cursor.execute(price_list_query,(stock_id,))
    prices = cursor.fetchall()
    return [prices[0] for price in prices]

#################################################################################################################################################################
# Function: get_inter_day_prices
# Parameters: cursor,selected_ticker
# get_inter_day_prices retrieves the prices and their corresponding dates from the inter_day stock table and returns them as a list for the graphing function to use to create a line graph
#
# output: price_list, date_list
#################################################################################################################################################################
def get_inter_day_prices(cursor,selected_ticker):
    stock_id = get_stock_id(cursor,selected_ticker)
    query = '''SELECT close, date FROM inter_day_prices WHERE stock_id = ? ORDER BY date ASC'''
    cursor.execute(query, (stock_id,))
    prices = cursor.fetchall()
    price_list = [price[0] for price in prices]
    date_list = [price[1] for price in prices]
    return price_list, date_list

#################################################################################################################################################################
# Function: get_stock_id
# Parameters: cursor,ticker
# get_stock_id gets the tickers corresponding stock id from the stocks table and returns it
#
# output: stock_id
#################################################################################################################################################################


def get_stock_id(cursor,ticker):
    id_query = '''SELECT id FROM stocks WHERE ticker = ?'''
    cursor.execute(id_query,(ticker,))
    stock_id = cursor.fetchone()
    if stock_id != None:
        return stock_id[0]
    else:
        return None
    
#################################################################################################################################################################
# Function: fetch_stock_prices
# Parameters: cursor,ticker
# fetch_stock_prices uses an alphavantage api to get an initial dataset to use to create a line graph for the corresponding ticker
# the data set is inserted into the inter_day stock table
# output: N/A
#################################################################################################################################################################
def fetch_stock_prices(cursor,ticker):
    
    global api_key
    stock_id = get_stock_id(cursor,ticker)
    if stock_id is None:
            print(f"Error: Ticker '{ticker}' not found in the database.")
            return
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'

    response = requests.get(url)
    data = response.json()
    # Extract daily prices
    daily_prices = data['Time Series (Daily)']
    for date, price_data in daily_prices.items():
        open_price = float(price_data['1. open'])
        high_price = float(price_data['2. high'])
        low_price = float(price_data['3. low'])
        close_price = float(price_data['4. close'])
        volume = int(price_data['5. volume'])

        print(f"Date: {date}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}")

        insert_inter_day_price_update(cursor, stock_id, open_price, close_price, high_price, low_price, date, volume)

#################################################################################################################################################################
# Function: get_recent_interday_stock_price
# Parameters: cursor,ticker
# get_recent_interday_stock_price 
#
# output:
#################################################################################################################################################################
def get_recent_interday_stock_price(cursor,ticker):
    global api_key
    stock_id = get_stock_id(cursor,ticker)
    if stock_id is None:
            print(f"Error: Ticker '{ticker}' not found in the database.")
            return
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    if 'Time Series (Daily)' in data:
        time_series = data['Time Series (Daily)']
        latest_date = list(time_series.keys())[0]
        latest_data = time_series[latest_date]
        open_price = latest_data['1. open']
        high_price = latest_data['2. high']
        low_price = latest_data['3. low']
        close_price = latest_data['4. close']
        volume = latest_data['5. volume']
        insert_inter_day_price_update(cursor, stock_id, open_price, close_price, high_price, low_price, latest_date, volume)

#################################################################################################################################################################
# Function: fetch_intraday_stock_prices
# Parameters: cursor,ticker
# 
#
# output:
#################################################################################################################################################################
def fetch_intraday_stock_prices(cursor,ticker):
    global api_key
    stock_id = get_stock_id(cursor,ticker)
    if stock_id is None:
            print(f"Error: Ticker '{ticker}' not found in the database.")
            return
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    pass

#################################################################################################################################################################
# Function: create_chart
# Parameters: dates, prices, ticker, root
# create_chart makes a line chart for the corresponding ticker
#
# output: line chart 
#################################################################################################################################################################
def create_chart(dates, prices, ticker, root):
    #pip install mplcursors
    # Convert date strings to datetime objects
    dates = [datetime.strptime(date, '%Y-%m-%d') for date in dates] #strips time from the date time object
    


    def plot_chart(dates,prices):
        fig = Figure(figsize=(5, 5), dpi=100) #size of the chart in inches
        ax = fig.add_subplot(111) 
        ax.plot(dates, prices, label=ticker)
        ax.set_title(f'Stock Prices for {ticker}')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.legend()

        # Formatting the x-axis to show dates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        fig.autofmt_xdate()  # Auto-format the x-axis dates for better display

        return fig,ax

    def update_chart(timeframe):
        #if timeframe == "daily"
            #query for daily data from DB
        #elif timeframe == "weekly"
            #query for weekly data from DB
        #elif timeframe == "monthly"
            #query for monthly data from DB


        #fig = plot_chart(new_dates, new_prices)
        #canvas.figure = fig
        #canvas.draw()
        pass
    


    fig,ax = plot_chart(dates,prices)
    
    cursor = mplcursors.cursor(ax, hover=True)
    prev_annotation = None
    prev_vline = None
    prev_hline = None
    @cursor.connect("add") #decorator in python that connects the on add function to the add event of the mplcursors.cursor object
    def on_add(sel):
        nonlocal prev_annotation, prev_vline, prev_hline
        if prev_annotation:
            prev_annotation.remove()
        if prev_vline:
            prev_vline.remove()
        if prev_hline:
            prev_hline.remove()


        date = mdates.num2date(sel.target[0]) #converts the numerical representation of a date time object -> (sel.target[0]) to an actual date time object
        price = sel.target[1] #set the y axis value to sel.target[1]

    # Set annotation text
        sel.annotation.set_text(f'{date.strftime("%Y-%m-%d")}, {price:.2f}')

        # Get the axes
        ax = sel.artist.axes

        # Draw dashed lines
        prev_vline = ax.axvline(x=sel.target[0], color='gray', linestyle='--', lw=0.5)
        prev_hline = ax.axhline(y=sel.target[1], color='gray', linestyle='--', lw=0.5)

        # Force a re-draw to remove the old lines and show the new ones
        
        plt.draw()
        
    chart_window = tk.Toplevel(root)
    chart_window.title("Stock Price Chart")
    def on_closing():
        nonlocal chart_window
        plt.close('all')  # Close all figures
        destroy_window(chart_window)
    chart_window.protocol("WM_DELETE_WINDOW", on_closing)

    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    button_frame = tk.Frame(chart_window)
    button_frame.pack(side=tk.BOTTOM)

    daily_button = tk.Button(button_frame, text="Daily", command=lambda: update_chart('daily'))
    daily_button.pack(side=tk.LEFT,padx=10)

    weekly_button = tk.Button(button_frame, text="Weekly", command=lambda: update_chart('weekly'))
    weekly_button.pack(side=tk.LEFT,padx=10)

    monthly_button = tk.Button(button_frame, text="Monthly", command=lambda: update_chart('monthly'))
    monthly_button.pack(side=tk.LEFT,padx=10)
    
#################################################################################################################################################################
# Function: add_ticker
# Parameters: cursor,root,mode_menu
# add_ticker creates a new window that allows a user to enter the ticker symbol ,the company name and url to the database
#
# output: N/A
#################################################################################################################################################################
def add_ticker(cursor,root,mode_menu):
    new_window = tk.Toplevel(root)
    new_window.title("Add Ticker")
    new_window.geometry("400x300")

    # Add widgets to the new window
    ticker_label = tk.Label(new_window, text="Ticker:")
    ticker_label.pack(pady=10)

    ticker_entry = tk.Entry(new_window)
    ticker_entry.pack(pady=10)
    

    ticker_entry_text = "Enter ticker symbol"
    ticker_entry.insert(0, ticker_entry_text)
    ticker_entry.config(fg='grey')

    company_name_entry = tk.Entry(new_window)
    company_name_entry.pack(pady=10)
    

    company_name_text = "company name"
    company_name_entry.insert(0, company_name_text)
    company_name_entry.config(fg='grey')

    

    url_entry = tk.Entry(new_window)
    url_entry.pack(pady=10)

    url_entry_text = "Yahoo URL"
    url_entry.insert(0, url_entry_text)
    url_entry.config(fg='grey')

    message_label = tk.Label(new_window, text="", fg='red')
    message_label.pack(pady=10)

    def on_focus_in(event, entry, placeholder):#click on the textbox will turn the text black
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event, entry, placeholder):
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    ticker_entry.bind("<FocusIn>", lambda event: on_focus_in(event, ticker_entry, ticker_entry_text))
    ticker_entry.bind("<FocusOut>", lambda event: on_focus_out(event, ticker_entry, ticker_entry_text))

    company_name_entry.bind("<FocusIn>", lambda event: on_focus_in(event, company_name_entry, company_name_text))
    company_name_entry.bind("<FocusOut>", lambda event: on_focus_out(event, company_name_entry, company_name_text))

    url_entry.bind("<FocusIn>", lambda event: on_focus_in(event, url_entry, url_entry_text))
    url_entry.bind("<FocusOut>", lambda event: on_focus_out(event, url_entry, url_entry_text))


    
    def check_url(url):
        try:
            response = requests.get(url)
            print(response.status_code)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def save_ticker():
        ticker = ticker_entry.get()
        company_name = company_name_entry.get()
        url = url_entry.get()
        if check_url(url):
            insert_stock(cursor, ticker, company_name, url)
            mode_menu['values'] = get_tickers(cursor)
            mode_menu.config(state='normal')
            mode_menu.current(0)
            message_label.config(text="Ticker added successfully!", fg='green')
            try:
                print("made it")
                fetch_stock_prices(cursor,ticker)
                fetch_intraday_stock_prices(cursor,ticker)
            except Exception as e:
                print(f"Error: {e}")
            new_window.destroy()
        else:
            message_label.config(text="Invalid URL. Please enter a valid URL.", fg='red')

    save_button = tk.Button(new_window, text="Save", command=save_ticker)
    save_button.pack(pady=10)

    
#################################################################################################################################################################
# Function: remove_ticker
# Parameters: cursor,mode_menu
# remove_ticker removes the selected ticker from the list then updates the list to reflect the change
#
# output: N/A
#################################################################################################################################################################    
def remove_ticker(cursor,mode_menu):
    selected_ticker = mode_menu.get()
    stock_id = get_stock_id(cursor,selected_ticker)
    delete_transactions_query = '''DELETE FROM transactions WHERE stock_id = ?'''
    delete_ticker_query = '''DELETE FROM stocks WHERE ticker = ?'''
    delete_inter_day_query = '''DELETE FROM inter_day_prices WHERE stock_id = ?'''
    cursor.execute(delete_transactions_query,(stock_id,))
    cursor.execute(delete_inter_day_query,(stock_id,))
    cursor.execute(delete_ticker_query, (selected_ticker,))
    cursor.connection.commit()

    remaining_tickers = get_tickers(cursor)
    if len(remaining_tickers) == 0:
        mode_menu['values'] = ["add a ticker"]
        mode_menu.set("add a ticker")
    else:
        mode_menu['values'] = remaining_tickers
        mode_menu.set(remaining_tickers[0])

#################################################################################################################################################################
# Function: select_a_ticker
# Parameters: cursor,mode_menu,root
# creates a new window where a user can see stats of the corresponding ticker and a list of their inputted transactions
#
# output: N/A
#################################################################################################################################################################
def select_a_ticker(cursor,mode_menu,root):
    if mode_menu.get() != "add a ticker":
        selected_ticker = mode_menu.get()
        
        #opens new window then shows statistics certain time periods amount of prices % change
        ticker_window = tk.Toplevel(root)
        ticker_window.title(selected_ticker)
        ticker_window.geometry("400x600")

        ticker_label = tk.Label(ticker_window, text=selected_ticker)
        ticker_label.pack(pady=10)

        price_list, date_list = get_inter_day_prices(cursor,selected_ticker)


        

        
    def show_ticker_info(ticker_window, selected_ticker):

        for widget in ticker_window.winfo_children():
            widget.destroy()

        #add data
        current_price = get_most_recent_interday_price(cursor,selected_ticker)
        current_price_label = tk.Label(ticker_window,text=f"Current Price: ${current_price:.2f}").pack(pady=5)
        average_price = get_average_price(cursor, selected_ticker)
        avg_price_label = tk.Label(ticker_window, text=f"Average Price: ${average_price:.2f}")
        avg_price_label.pack(pady=5)

        # Fetch and display the gain/loss
        current_diff = get_current_diff(cursor, selected_ticker)
        gain_loss_label = tk.Label(ticker_window, text=f"Gain/Loss: {current_diff:.2f}%")
        gain_loss_label.pack(pady=5)

        profit = get_profit(cursor,selected_ticker)
        profit_label = tk.Label(ticker_window, text=f"Profit/Loss: {profit:.2f}$")
        profit_label.pack(pady=5)

        transactions_listbox = tk.Listbox(ticker_window, width=80, height=10)
        transactions_listbox.pack(pady=10)

        add_button = tk.Button(ticker_window, text="Add Transaction", command=lambda: add_transaction(cursor, ticker_window,selected_ticker,transactions_listbox))
        add_button.pack(side='top', padx=0)
        notify_button = tk.Button(ticker_window, text="Set Notifications", command=lambda: show_notification_settings(ticker_window,selected_ticker))
        notify_button.pack(side='top', pady=5)
        chart_button = tk.Button(ticker_window, text="See Chart", command=lambda: create_chart(date_list, price_list, selected_ticker, root))
        chart_button.pack(side = 'top',pady=5)
        back_button = tk.Button(ticker_window, text="Back", command=lambda: destroy_window(ticker_window))
        back_button.pack(side = 'top',pady=5)
        

        

        transactions = get_transactions(cursor,selected_ticker)
        
        if transactions != None:
            for i in range(len(transactions)):
                transactions_listbox.insert(tk.END, f"Type: {transactions[i][0]}, Quantity: {transactions[i][1]}, Price: {transactions[i][2]}, Date: {transactions[i][3]}")
        else:
            return


        
       
       



    def show_notification_settings(window, selected_ticker):
        # Clear the window
        
        for widget in window.winfo_children():
            widget.destroy()

        # Add new widgets for notification settings
        tk.Label(window, text="Notification Settings").pack(pady=10)
        

        interval_var = tk.StringVar()
        interval_label = tk.Label(window, text="Interval Length")
        interval_label.pack()

        interval_menu = ttk.Combobox(window, textvariable=interval_var)
        interval_menu['values'] = ('30 min ', '1 hour', '2 hour')
        interval_menu.current(0)
        interval_menu.pack()

        #tk.Label(window, text="Interval:").pack(pady=5)
        #interval_entry = tk.Entry(window)
        #interval_entry.pack(pady=5)

        percent_var = tk.StringVar()
        percent_label = tk.Label(window, text="Percent Change")
        percent_label.pack()

        percent_change_menu = ttk.Combobox(window, textvariable=percent_var)
        percent_change_menu['values'] = ('5 ', '10', '15')
        percent_change_menu.current(0)
        percent_change_menu.pack()

        #tk.Label(window, text="Percent Change Threshold:").pack(pady=5)
        #percent_entry = tk.Entry(window)
        #percent_entry.pack(pady=5)

        var = tk.BooleanVar()
        toggle_button = tk.Checkbutton(window, text='Track', variable=var, command=lambda:on_toggle(var))
        toggle_button.pack()
        
        def on_toggle(var):
            print(f'Tracking: {var.get()}')

        def save_settings():
            interval = interval_var.get()
            percent_change = percent_var.get()
            tracking = var.get()
            
            if not interval and not percent_change:
                messagebox.showerror("Error", "Either interval or percent change threshold must be entered to enable tracking.")
                return
            def add_tracking_entry(cursor, selected_ticker, tracking, interval, percent_change):
                stock_id = get_stock_id(cursor,selected_ticker)
                tracking_query = '''SELECT tracking FROM stock_tracking WHERE stock_id = ?'''
                cursor.execute(tracking_query,(stock_id,))
                trackingDB = cursor.fetchone()
                if trackingDB: #if we already have an entry
                    update_tracking(cursor, stock_id, tracking, interval, percent_change)
                else:
                    insert_tracking(cursor, stock_id, tracking, interval, percent_change)


            add_tracking_entry(cursor, selected_ticker, tracking, interval, float(percent_change))
            try:
                if not interval:
                    send_email("Notification settings confirmed",f"Saved setting: Percent Change: {percent_change}","kammerma@ualberta.ca")
                elif not percent_change:
                    send_email("Notification settings confirmed",f"Saved settings: Interval: {interval}","kammerma@ualberta.ca")
                else:
                    send_email("Notification settings confirmed",f"Saved settings: Interval: {interval}, Percent Change: {percent_change}","kammerma@ualberta.ca")
            except:
                messagebox.showinfo("Could not send email")

            
            show_ticker_info(window, selected_ticker) 
        
        tk.Button(window, text="Save", command=save_settings).pack(pady=20)

        tk.Button(window, text="Back", command=lambda: show_ticker_info(window, selected_ticker)).pack(pady=5)
    show_ticker_info(ticker_window, selected_ticker)    
#################################################################################################################################################################
# Function: add_transaction
# Parameters: cursor,root,selected_ticker,transactions_listbox
# add_transaction creates a new window that allows a user to add a new transaction to the database 
#
# output: N/A
#################################################################################################################################################################
def add_transaction(cursor,root,selected_ticker,transactions_listbox):
    transaction_window = tk.Toplevel(root)
    transaction_window.title("Enter Transaction")
    transaction_window.geometry("400x300")

    unit_text_entry = tk.Entry(transaction_window) #creates text box
    unit_text_entry.pack(pady=10)
    
    unit_text = "Units"
    unit_text_entry.insert(0, unit_text)
    unit_text_entry.config(fg='grey')
    
    price_text_entry = tk.Entry(transaction_window) #creates text box
    price_text_entry.pack(pady=10)
    
    price_text = "Price"
    price_text_entry.insert(0, price_text)
    price_text_entry.config(fg='grey')

    mode_var = tk.StringVar()
    mode_label = tk.Label(transaction_window, text="Transaction Type")
    mode_label.pack()

    mode_menu = ttk.Combobox(transaction_window, textvariable=mode_var)
    mode_menu['values'] = ('Buy', 'Sell')
    mode_menu.current(0)
    mode_menu.pack(pady = 10)


    def on_focus_in(event, entry, placeholder):#click on the textbox will turn the text black
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(event, entry, placeholder):
        if entry.get() == '':
            entry.insert(0, placeholder)
            entry.config(fg='grey')

    unit_text_entry.bind("<FocusIn>", lambda event: on_focus_in(event, unit_text_entry, unit_text))
    unit_text_entry.bind("<FocusOut>", lambda event: on_focus_out(event, unit_text_entry, unit_text))

    price_text_entry.bind("<FocusIn>", lambda event: on_focus_in(event, price_text_entry, price_text))
    price_text_entry.bind("<FocusOut>", lambda event: on_focus_out(event, price_text_entry, price_text))

    confirm_button = tk.Button(transaction_window, text="Confirm Transaction", command=lambda: confirm_transaction(cursor, transaction_window,selected_ticker,mode_menu, transactions_listbox))
    confirm_button.pack(pady = 5)

    back_button = tk.Button(transaction_window, text="Back", command=lambda: destroy_window(transaction_window))
    back_button.pack(side = 'bottom',pady=5)

    def confirm_transaction(cursor, transaction_window, selected_ticker, mode_menu, transactions_listbox):
        stock_id = get_stock_id(cursor,selected_ticker)
        price = price_text_entry.get()
        units = unit_text_entry.get()
        timestamp_now = datetime.now()
        transaction_type = mode_menu.get()
        cursor.execute('''INSERT INTO transactions (stock_id, transaction_type, quantity, price, transaction_date)
                  VALUES (?, ?, ?, ?, ?)''', 
               (stock_id, transaction_type, units, price, timestamp_now))
        cursor.connection.commit()
        refresh_listbox(cursor, selected_ticker, transactions_listbox)
    
#################################################################################################################################################################
# Function: destroy_window
# Parameters: window - current window in the gui
# destroy_window delets the current window in selection
#
# output: N/A
#################################################################################################################################################################
def destroy_window(window):
        window.destroy()

#################################################################################################################################################################
# Function: refresh_listbox
# Parameters: cursor, ticker, transactions_listbox
# refresh_listbox takes a list of transactions and repopulates the list to create an effect of realtime updating a list
#
# output: N/A
#################################################################################################################################################################
def refresh_listbox(cursor, ticker, transactions_listbox):
    # Clear existing items
    transactions_listbox.delete(0, tk.END)
    
    # Fetch updated transactions
    transactions = get_transactions(cursor, ticker)
    
    # Insert updated transactions into the Listbox
    for transaction in transactions:
        transactions_listbox.insert(tk.END, f"Type: {transaction[0]}, Quantity: {transaction[1]}, Price: {transaction[2]}, Date: {transaction[3]}")

#################################################################################################################################################################
# Function: get_rsi
# Parameters: Work in progress
#
#
# output:
#################################################################################################################################################################
def get_rsi(cursor,selected_ticker):
    
    RS = get_average_change(cursor,selected_ticker)
    if (RS > 0):
        RSI = 100 - ( 100 / (1+RS))
        return RSI
    else:
        return 100

   

#################################################################################################################################################################
# Function: get_average_change
# Parameters: Work in progress
#
#
# output:
#################################################################################################################################################################
def get_average_change(cursor,selected_ticker):
    close_prices = get_interday_closing_prices(cursor,selected_ticker)
    deltas = [close_prices[i] - close_prices[i - 1] for i in range(1, len(close_prices))]
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    average_gain = sum(gains)/len(gains)
    average_loss = sum(losses)/len(losses)
    if average_loss == 0: #avoid division by 0
        return 0
    RS = average_gain/average_loss
    return RS

#################################################################################################################################################################
# Function: get_interday_closing_prices
# Parameters: cursor,selected_ticker
# get_interday_closing_prices gets the most 15 most recent closing day prices but in chronological order
#
# output: close_prices list
#################################################################################################################################################################
def get_interday_closing_prices(cursor,selected_ticker):
    stock_id = get_stock_id(selected_ticker)
    closing_price_query = '''SELECT close FROM inter_day_prices_table WHERE stock_id = ? ORDER BY date DESC LIMIT 15'''
    cursor.execute(closing_price_query,(stock_id,))
    rows = cursor.fetchall()
    close_prices = [row[0] for row in rows]
    return close_prices.reverse() #need the last 15 days but in chronological order

#################################################################################################################################################################
# Function: get_transactions
# Parameters: cursor,ticker
# get_transactions retrieves a list of transactions of both buy and sells the user has inputted into the database
#
# output: transactions - list
#################################################################################################################################################################
def get_transactions(cursor,ticker):
    stock_id = get_stock_id(cursor,ticker)
    transactions_query = '''Select transaction_type, quantity, price, transaction_date FROM transactions WHERE stock_id = ?'''
    cursor.execute(transactions_query,(stock_id,))
    rows = cursor.fetchall()
    transactions = [row for row in rows]
    return transactions

#################################################################################################################################################################
# Function: get_tickers
# Parameters: cursor
# get_tickers retrieves a list of tickers the user has entered into the database 
#
# output: ticker_list
#################################################################################################################################################################
def get_tickers(cursor):
    ticker_query = '''SELECT DISTINCT ticker FROM stocks'''
    cursor.execute(ticker_query)
    tickers = cursor.fetchall()
    ticker_list = [ticker[0] for ticker in tickers]
    return ticker_list

#################################################################################################################################################################
# Function: get_average_price
# Parameters: cursor,ticker
# get_average_price computes the average price of the stock the user has bought in at, for the corresponding ticker
#
# output: average_price
#################################################################################################################################################################
def get_average_price(cursor,ticker):
    #transactions_listbox.insert(tk.END, f"Type: {transactions[i][0]}, Quantity: {transactions[i][1]}, Price: {transactions[i][2]}, Date: {transactions[i][3]}")
    transactions = get_transactions(cursor,ticker)
    total_cost = 0
    total_units = 0
    average_price = 0
    if(len(transactions) > 0):
        for i in range(len(transactions)):
            if transactions[i][0] == "Buy":
                total_cost += transactions[i][1] * transactions[i][2] #quantity * price
                total_units += transactions[i][1]
            else:
                total_cost -= transactions [i][1] * transactions[i][2]
                total_units -= transactions[i][1]
        average_price = total_cost/total_units
        return average_price
    else:
        return average_price

#################################################################################################################################################################
# Function: get_profit
# Parameters: cursor,ticker
# get_profit computes the overall profit a user has made or lost on the corresponding ticker
#
# output: profit
#################################################################################################################################################################    
def get_profit(cursor,ticker):
    transactions = get_transactions(cursor,ticker)
    cost = 0
    revenue = 0
    quantity_bought = 0
    quantity_sold = 0
    profit = 0
    current_price = get_most_recent_interday_price(cursor,ticker)
    for i in range(len(transactions)):
        if transactions[i][0] == "Buy":
            cost += transactions[i][1] * transactions[i][2] #quantity * price
            quantity_bought  += transactions[i][1]
        else: #sold
            revenue += transactions [i][1] * transactions[i][2]
            quantity_sold += transactions[i][1]
    #print(revenue)
    #print(cost)
    profit = (revenue - cost) + ((quantity_bought-quantity_sold) * current_price)
    return profit

#################################################################################################################################################################
# Function: get_interval
# Parameters: cursor,ticker
# get_interval retrieves the interval set by the user in the database
#
# output: interval - string
#################################################################################################################################################################
def get_interval(cursor,ticker):
    stock_id = get_stock_id(cursor,ticker)
    interval_query = '''SELECT interval FROM stock_tracking WHERE stock_id = ?'''
    cursor.execute(interval_query,(stock_id,))
    row = cursor.fetchone()
    if row is not None:
        return row[0]
    else:
        return None
    
#################################################################################################################################################################
# Function: get_percent_change_threshold
# Parameters: cursor,ticker 
# get_percent_change_threshold retrieves the percent change threshold the user has set in the database
#
# output: percent change threshold
#################################################################################################################################################################    
def get_percent_change_threshold(cursor,ticker):
    stock_id = get_stock_id(cursor,ticker)
    perecent_change_query = '''SELECT percent_change_threshold FROM stock_tracking WHERE stock_id = ?'''
    cursor.execute(perecent_change_query,(stock_id,))
    row = cursor.fetchone()
    if row is not None:
        return row[0]
    else:
        return None


#################################################################################################################################################################
# Function: get_open_price
# Parameters: cursor,ticker
# get_open_price retrieves the most recent open price from the interday table
#
# output: open price - float
#################################################################################################################################################################
def get_open_price(cursor,ticker):
    stock_id = get_stock_id(cursor,ticker)
    open_price_query = '''SELECT open FROM inter_day_prices WHERE stock_id = ? ORDER BY date DESC LIMIT 1'''
    cursor.execute(open_price_query,(stock_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"No open price found for ticker {ticker}")
        return None
    
    return row[0]

#################################################################################################################################################################
# Function: get_url
# Parameters: cursor,ticker
# retrieves the stock url for the corresponding ticker in the stocks table
#
# output: url = string
#################################################################################################################################################################
def get_url(cursor,ticker):
    stock_id = get_stock_id(cursor,ticker)
    url_query = '''SELECT url FROM stocks WHERE id = ?'''
    cursor.execute(url_query,(stock_id,))
    row = cursor.fetchone()
    if row is not None:
        return row[0]  
    else:
        return None
    
#################################################################################################################################################################
# Function: get_most_recent_intraday_price
# Parameters: cursor,ticker
# retrieves the most recent intraday price from the intra day stock table
#
# output: price
#################################################################################################################################################################    
def get_most_recent_intraday_price(cursor,ticker):
    stock_id = get_stock_id(cursor,ticker)
    most_recent_intraday_price_query = '''SELECT price FROM intra_day_prices WHERE stock_id = ? ORDER BY timestamp DESC LIMIT 1'''
    cursor.execute(most_recent_intraday_price_query,(stock_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"No price found for ticker {ticker}")
        return None
    return row[0]

#################################################################################################################################################################
# Function: get_most_recent_interday_price
# Parameters: cursor, ticker
# 
#
# output:
#################################################################################################################################################################
def get_most_recent_interday_price(cursor,ticker):
    stock_id = get_stock_id(cursor,ticker)
    most_recent_intraday_price_query = '''SELECT close FROM inter_day_prices WHERE stock_id = ? ORDER BY date DESC LIMIT 1'''
    cursor.execute(most_recent_intraday_price_query,(stock_id,))
    row = cursor.fetchone()
    if row is None:
        print(f"No price found for ticker {ticker}")
        return None
    return row[0]

#################################################################################################################################################################
# Function: get_current_diff
# Parameters: cursor,ticker
# get_current_diff gets the current % gain or loss from the users average price
#
# output: diff - float
#################################################################################################################################################################
def get_current_diff(cursor,ticker):
    current_price = get_most_recent_interday_price(cursor,ticker)
    print(current_price)
    average_price = get_average_price(cursor,ticker)
    if average_price == 0:  # Prevent division by zero
        return 0
        
    diff = ((current_price - average_price) / average_price) * 100
    return diff


    

#################################################################################################################################################################
# Function: main
# Parameters: N/A
# main creates the main window for the app
#
# output: N/A
#################################################################################################################################################################
def main():
    path = "./stockdb.db"
    connection, cursor = db_connect(path) #connect to DB
    ticker_list = get_tickers(cursor)
    if len(ticker_list) != 0: #update interday for graph
        for ticker in ticker_list:
            get_recent_interday_stock_price(cursor,ticker)

    #Setting up the GUI
    root = tk.Tk()
    root.title("StockWatch")
    root.geometry("500x300")
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)
    # Create a dropdown menu for mode selection

    mode_var = tk.StringVar()
    mode_label = tk.Label(frame, text="Select a Stock:")
    mode_label.pack(side='left')

    mode_menu = ttk.Combobox(frame, textvariable=mode_var)
    
    if ticker_list:
        mode_menu['values'] = ticker_list
        mode_menu.current(0)
    else:
        mode_menu['values'] = ["add a ticker"]
        mode_menu.current(0)
        mode_menu.config(state='disabled')
    mode_menu.pack(side ='left', padx=5)

    # Create buttons to start, stop, and pause the bot
    add_button = tk.Button(frame, text="Add Ticker", command=lambda: add_ticker(cursor, root, mode_menu))
    add_button.pack(side='right', padx=5)

    remove_button = tk.Button(frame, text="Remove Ticker", command=lambda: remove_ticker(cursor,mode_menu))
    remove_button.pack(side='right', padx=5)

    select_button = tk.Button(root, text="Select ", command=lambda: select_a_ticker(cursor,mode_menu,root),width = 20,height= 1)
    select_button.pack(side='bottom')

    # Run the GUI loop
    root.mainloop()

    connection.close()
if __name__ == "__main__":
    main()

