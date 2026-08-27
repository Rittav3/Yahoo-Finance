# Get Bitkub historial price (daily)

import time
import requests
import pandas as pd

# Define endpoint and parameters
url = 'https://api.bitkub.com/tradingview/history'
savepath = '~/Amibroker Data/Raw Data/'
savefile  =savepath + 'Bitkub_BTC.csv'
# Calculate timestamps (e.g., last 7 days)
backday = 20


to_time = int(time.time())
#from_time = to_time - (backday * 24 * 60 * 60)   , not use due to use since  it has data

params = {
    'symbol': 'BTC_THB',  # Trading pair
    'resolution': '1D',  # Interval: 1, 5, 15, 60, 240, 1D
    'from': 1,  # Start timestamp
    'to': to_time,  # End timestamp
}

# Make GET request
response = requests.get(url, params=params)
data = response.json()

# Check status and print results
df=pd.DataFrame(data)

print('Bitkub BTC has data Days :')
print (df.shape[0])


df['datetime'] = pd.to_datetime(df['t'], unit='s').dt.tz_localize('UTC').dt.tz_convert('Asia/Bangkok').dt.tz_localize(None)
df['datetime'] = df['datetime'].dt.strftime("%Y-%m-%d")
df.drop(['s','t'],axis=1, inplace=True)
df['Ticker'] = 'Bitkub_BTC'
df['Adj Close'] = df['c']
df = df[['datetime','Ticker','o','h','l','c','v','Adj Close' ]]
df.columns = ['Date','Ticker','Open','High','Low','Close','Volume', 'Adj Close']

df.to_csv(savefile,index=False)

