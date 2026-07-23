# %%
# Set up all file path here:
from pathlib import Path

# use folder 'Downloads' as default
download_folder = str(Path.home() / "Downloads")

mvrv_file = download_folder + '\\mvrv.json'
savefile = download_folder + '\\downloadMVRV.csv'
BitcoinMVRV_file = '~\\Amibroker Data\\Raw Data\\BitcoinMVRV.csv' # load existing MVRV file to combine with downloadMVRF.csv
# save_final_BitcoinM_combined_file = download_folder + '\\BitcoinMVRV_combine.csv'
save_final_BitcoinMVRV_combined_file = BitcoinMVRV_file # overwrite to existing file

# %%
# Step 1: Delete old mvrv.json files in Downloads folder

def delete_matching_files_in_downloads():
    """
    Finds the user's Downloads folder and deletes files that match a specific pattern.
    """
    try:
        downloads_path = Path.home() / "Downloads"
        if not downloads_path.is_dir():
            print(f"Error: The Downloads folder was not found at '{downloads_path}'")
            return

        print(f"Searching for files in: {downloads_path}")
        files_found = list(downloads_path.glob('mvrv*.json'))

        if not files_found:
            print("No files found matching the pattern 'mvrv*.json'. Nothing to delete.")
            return

        print(f"Found {len(files_found)} file(s) to delete:")
        for file_path in files_found:
            print(f" - {file_path.name}")

        for file_path in files_found:
            try:
                file_path.unlink()  # Deletes the file
                print(f"Successfully deleted: {_path.name}")
            except OSError as e:
                print(f"Error deleting file {file_path.name}: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    delete_matching_files_in_downloads()

# %%
# STEP 2: Click download button on webpage using Playwright
from playwright.sync_api import Playwright, sync_playwright, expect
import time

def run_automation():
    # Launch browser (headless=False allows you to see the window)
    with sync_playwright() as p:
        # You can use chromium, firefox, or webkit
        browser = p.chromium.launch(headless=False) 
        context = browser.new_context()
        page = context.new_page()

        try:
            # Step 1: Open the web page
            page.goto("https://www.blockchain.com/explorer/charts/mvrv")
            
            # Wait for a short time to allow page load (similar to your original script)
            time.sleep(5)

            # Step 2: Locate and click the button using XPath
            # Playwright's locator handles waiting automatically for element visibility

            with page.expect_download() as download_info:
                page.get_by_text("Download JSON").click()
            download = download_info.value
            download.save_as(mvrv_file)
            print('download to : '+ mvrv_file)


            print("Button clicked successfully via Playwright.")
            
            # Optional: wait to observe result
            time.sleep(3)

        except Exception as e:
            print(f"An error occurred during automation: {e}")
        finally:
            browser.close()

run_automation()

# %%
# STEP 3: Read JSON and make CSV file
import json
import pandas as pd
from datetime import datetime

# Load JSON data
with open(mvrv_file, 'r') as f:
    data = json.load(f)

# Extract MVRV data
mvrv_data = data['mvrv']

# Convert to DataFrame
df = pd.DataFrame(mvrv_data)

# Convert timestamp from milliseconds to datetime
df['timestamp'] = pd.to_datetime(df['x'], unit='ms')
df['mvrv'] = df['y']

# Reorder and clean up
df = df[['timestamp', 'mvrv']]




# %%
df['Date'] = df['timestamp'].dt.date
#df_daily =df.groupby('date').agg({'mvrv': 'mean'}).reset_index()
df_mvrv_daily =df.groupby('Date').mean().reset_index()

#madfe open hi low close ... use same value as MVRV value
# df_mvrv_daily['mvrv'] => this colume is MVRV value
df_mvrv_daily['Ticker'] = 'Bitcoin-MVRV'
df_mvrv_daily['Open'] = df_mvrv_daily['mvrv'] 
df_mvrv_daily['High'] = df_mvrv_daily['mvrv']
df_mvrv_daily['Low'] = df_mvrv_daily['mvrv']
df_mvrv_daily['Close'] = df_mvrv_daily['mvrv']      
df_mvrv_daily['Volume'] = 0
df_mvrv_daily['Adj Close'] = df_mvrv_daily['mvrv']
df_mvrv_daily.drop(['mvrv','timestamp'], axis=1, inplace=True)



# %%
df_mvrv_daily.to_csv(savefile,index=False)
print('save file to :' + savefile)
del df, df_mvrv_daily

# %%
#STEP 4 load existing MVRV.csv and merge with new downloadMVRV.csv

# %%

df_bitcoin_mvrv = pd.read_csv(BitcoinMVRV_file)
df_download_mvrv = pd.read_csv(savefile)

# %%
# 2. Concatenate the two DataFrames.
combined_df = pd.concat([df_bitcoin_mvrv, df_download_mvrv], ignore_index=True)
# 3. Remove duplicates from the 'date' column, keeping the first entry.
del df_bitcoin_mvrv , df_download_mvrv
df_BitcoinMVRV = combined_df.drop_duplicates(subset=['Date'], keep='first')
df_BitcoinMVRV.dropna()
#df_BitcoinMVRV.sort_values(by='date', inplace=True)

df_BitcoinMVRV.to_csv(save_final_BitcoinMVRV_combined_file,index=False)
print ('Save MVRV file to :' + save_final_BitcoinMVRV_combined_file)

# %%
#delete mvrv.json, downloadMVRV.csv


# %%
import os

# %%
try:
    os.remove(mvrv_file)
except Exception as e:
    print(f"Error: Deleted File not found at path: {download_folder}")
try:
    os.remove(savefile)
except Exception as e:
    print(f"Error: Deleted File not found at path: {download_folder}")

print('All done')

# %%

