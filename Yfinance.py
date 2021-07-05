
#!/home/home/miniconda3/bin/python
#!usr/bin/env python3.8
# %%

#pip install -i https://pypi.anaconda.org/ranaroussi/simple yfinance
import yfinance as yf


# %%
# Set the start and end date
savepath = '~/Amibroker Data/Raw Data/'
start_date = '2000-01-01'
end_date = '2040-12-31'


# %%
stock = { '^GSPC':'S&P500',
         '^IXIC':'NASDAQ',
         '^DJI':'DOW30',
         'BTC-USD':'BitcoinUSD',
         'ETH-USD':'ETH-USD',
         'BNB-USD':'BNB-USD',
         '^FTSE':'FTSE100',
         '^VIX':'VIX',
         '^N225':'NIKKEI225',
         '^HSI':'HSI',
         '^STI':'STI',
         '^BSESN':'BSE SENSEX',
         '399001.SZ':'SHENZHEN',
         '^TWII':'TSEC',
         'DOGE-USD':'DOGE-USD',
         'GC=F':'GOLD'
 
        }


# %%



# %%
# for count stock to be download
stock_count = len(stock)
i=0

# main process
for ticker in stock:
    i=i+1
    stockname = stock[ticker]
    process_msg = 'Process '+ str(i)+ ' of '+ str(stock_count) + ' : ' +  stockname
    print (process_msg)
    savename = savepath + stockname + '.csv'
    data = yf.download(ticker, start_date, end_date)
    data['ticker'] = stockname
    data = data.reindex(columns=['ticker','Open','High','Low','Close','Volume','Adj Close'])
    
    
    data.to_csv(savename)
    

print ('Done ...')

# %%


# %%


# %%



