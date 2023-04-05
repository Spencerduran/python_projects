import pandas as pd
import yfinance as yf

#minute_data = msft.download(tickers="MSFT", period="5d", interval="1m")
ticker = "SPY"
def pull_data(ticker):
    minute_data = yf.download(ticker, interval="1m", period="5d")
    hour_data = yf.download(ticker, interval="60m", period="5d")
    minute_data.to_csv('minute_data.csv', encoding='utf-8') # False: not include index
    hour_data.to_csv('hour_data.csv', encoding='utf-8') # False: not include index


def data_by_day(minute_data, hour_data):
    minute_data['Datetime']=pd.to_datetime(minute_data['Datetime'])
    hour_data['Datetime']=pd.to_datetime(hour_data['Datetime'])
    days_by_minute = (minute_data.groupby(by=minute_data['Datetime'].dt.date))
    days_by_hour = (hour_data.groupby(by=hour_data['Datetime'].dt.date))
    return days_by_minute,days_by_hour

                
def calculate_idr(days_by_minute, days_by_hour):
    for day in days_by_hour:
        date = day[0]
        day_data = day[1]
        for column, row in day_data.iterrows():
            time = str(row["Datetime"])[-8:-3]
            if time == "09:30":
                first_hour_open = round(row["Open"], 2)
                first_hour_close = round(row["Close"], 2)
                rdr_high = round(row["High"], 2)
                rdr_low = round(row["Low"], 2)
                if first_hour_open > first_hour_close:
                    ridr_high = first_hour_open
                    ridr_low = first_hour_close
                elif first_hour_open == first_hour_close:
                    ridr_high = first_hour_open
                    ridr_low = first_hour_open
                else:
                    ridr_low = first_hour_open
                    ridr_high = first_hour_close
                print(f"Day: {date}:\n\
                        DR High: {rdr_high}\
                        IDR High: {ridr_high}\
                        IDR Low: {ridr_low}\
                        DR Low: {rdr_low}\
                      ")
    return rdr_high,ridr_high,ridr_low,rdr_low
#    for day in days_by_minute:
#        print(day)
#        for row, column in day.iterrows():
#                hour = column['Datetime'].hour
#                print(hour)
                ##timestamp = date_time[-8:]
                ##print(timestamp)
#    print(f"\n\n\n\n{column}\n{row}\n")

    #print(type(splitframe))
    #for day in splitframe:
    #    for row, column in minute_data.iterrows():
    #            hour = column['Datetime'].hour
    #            minute = column['Datetime'].minute
    #            print(hour, minute)


def main():
#    pull_data(ticker)
    minute_data = pd.read_csv('minute_data.csv')  
    hour_data = pd.read_csv('hour_data.csv')  
    days_by_minute, days_by_hour = data_by_day(minute_data, hour_data)
    calculate_idr(days_by_minute, days_by_hour)
    


    #calculate_dr_levels(minute_data)


if __name__ == "__main__":
#@    parser = argparse.ArgumentParser(description='')
#@    parser.add_argument('-compare_columns', action='store_true')
#@    args = parser.parse_args()
    main()
