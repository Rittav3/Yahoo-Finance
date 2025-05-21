# %%
from yahoofinancials import YahooFinancials
import yfinance as yf
import pandas as pd
import requests
import numpy as np

# %%
savepath = '~/Amibroker Data/Raw Data/'
startdate = '2000-01-01'
enddate = '2040-12-31'

# %%
stock = { '^GSPC':'S&P500',
         '^IXIC':'NASDAQ',
         '^DJI':'DOW30',
         'BTC-USD':'BitcoinUSD',
         'ETH-USD':'ETH-USD',
         'BNB-USD':'BNB-USD',
         'XRP-USD':'XRP-USD',
         '^FTSE':'FTSE100',
         '^VIX':'VIX',
         '^N225':'NIKKEI225',
         '^HSI':'HSI',
         '^STI':'STI',
         '^BSESN':'BSE SENSEX',
         '399001.SZ':'SHENZHEN',
         '^TWII':'TSEC',
         'DOGE-USD':'DOGE-USD',
         '^TNX':'10YearBond',
         '^CMC200':'CMC Crypto200',
         'EURUSD=X':'EUR-USD',
         'USDTHB=X':'USD-THB',
         'SHIB-USD':'SHIBA-USD',
         'BABYDOGE-USD':'BABYDOGE-USD',
         'GC=F':'GOLD',
         'AAPL':'AAPL80',
         'MSFT':'MSFT80',
         'NFLX':'NFLX80',
         'GOOG' : 'GOOG80',
         'NVDA' : 'NVDA80',
         'SBUX' : 'SBUX80',
         'AMZN' : 'AMZN80',
         'META' : 'META80',
         'KO' : 'KO80',
         'PEP' : 'PEP80',
         'BRK-B' :'BRKB80',
         'XLM-USD' : 'XLM-USD',
         'XRP-USD' : 'XRP-USD',
         'ETH-BTC' : 'ETH-BTC',
         'SOL-USD' : 'SOL-USD',
         'TSLA' : 'TLSA80',
         'BABA' : 'BABA80',
         '0700.HK' : 'TENCENT80',
         'RMS.PA' : 'HERMES80',
         'NTDOY' : 'NINTENDO19',
         'MC.PA' : 'LVMH01'
         
 
        }

# %%
stock_count = len(stock)
i=0

# main process
for ticker in stock:
    i=i+1
    stockname = stock[ticker]
    process_msg = 'Process '+ str(i)+ ' of '+ str(stock_count) + ' : ' +  stockname
    print (process_msg)
    data = yf.download(ticker,start=startdate,auto_adjust=False)
    data = data.xs(ticker,axis=1,level='Ticker')
    data['Ticker'] = stockname
    data = data.reindex(columns=['Ticker','Open','High','Low','Close','Volume','Adj Close'])

    savename = savepath + stockname+'.csv'
    print('save file : '+ savename)
    data.to_csv(savename, index=True)

# %%
# Create Bitcoin THB
print ('Create table BitCoin-THB by multiply CloseTHB to all BTC open hi low close')


btc_data = savepath +'BitcoinUSD.csv'
thb_data = savepath + 'USD-THB.csv'
save_BTC_THB = savepath + 'BitcoinTHB.csv'

df_btc = pd.read_csv(btc_data)
df_thb = pd.read_csv(thb_data)
df_thb['CloseTHB'] = df_thb['Adj Close']  # add column Close-THB as new col name

# merge BTC as main table and add THB ( BTC has less row )
df_btc_thb = pd.merge(df_btc, df_thb[['Date','CloseTHB']],on='Date', how='left')

# multiply exist BTC data with USB-THB(close)
df_btc_thb['Open'] = df_btc_thb['Open'] * df_btc_thb['CloseTHB'] 
df_btc_thb['High'] = df_btc_thb['High'] * df_btc_thb['CloseTHB'] 
df_btc_thb['Low'] = df_btc_thb['Low'] * df_btc_thb['CloseTHB'] 
df_btc_thb['Close'] = df_btc_thb['Close'] * df_btc_thb['CloseTHB'] 
df_btc_thb['Adj Close'] = df_btc_thb['Adj Close'] * df_btc_thb['CloseTHB'] 

df_btc_thb['Ticker']  = 'BitcoinTHB'
df_btc_thb.drop('CloseTHB', axis=1, inplace=True)
df_btc_thb.dropna(inplace=True)

df_btc_thb.to_csv(save_BTC_THB, index=False)

print ('Created BTC-THB Done')

print ('Made Bitcoin/SP5oo index begin')
BTC_file = savepath +'BitcoinUSD.csv'
SP500_file = savepath + 'S&P500.csv'

df_BTC = pd.read_csv(BTC_file)
df_SP500 = pd.read_csv(SP500_file)
df_BTC_SP500 = pd.merge(df_SP500,df_BTC,on= 'Date', how='left').dropna()
df_BTC_SP500['ticker']  ='.BTC_SP500'
df_BTC_SP500['Open'] = df_BTC_SP500['Open_y'] / df_BTC_SP500['Open_x']
df_BTC_SP500['High'] = df_BTC_SP500['High_y'] / df_BTC_SP500['High_x']
df_BTC_SP500['Low'] = df_BTC_SP500['Low_y'] / df_BTC_SP500['Low_x']
df_BTC_SP500['Close'] = df_BTC_SP500['Close_y'] / df_BTC_SP500['Close_x']
df_BTC_SP500['Volumn'] = df_BTC_SP500['Volume_y'] / df_BTC_SP500['Volume_x']
df_BTC_SP500['Adj Close'] = df_BTC_SP500['Adj Close_y'] / df_BTC_SP500['Adj Close_x']
df_BTC_SP500.drop(df_BTC_SP500.iloc[:, 1:15], inplace=True, axis=1)
savefile_BTC_SP500  =savepath + 'BTC_SP500.csv'
df_BTC_SP500.to_csv(savefile_BTC_SP500, index=False)
print('made index BTC/SP500 Done!')

print(" ")
print ('All Done !!')


