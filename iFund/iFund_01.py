import asyncio
import os
import re
from click import Path
from playwright.async_api import Playwright, async_playwright, expect

from pathlib import Path
import pandas as pd
import os
import glob



class ifundrobot:
    def __init__(self, playwright: Playwright, headless: bool = False):
        self.playwright = playwright
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

        self.download_folder = ifund_savefolder
        

    async def open_main_page(self) -> None:
        self.browser = await self.playwright.chromium.launch(headless=self.headless) 
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        await self.page.goto("https://www.krungsrisecurities.com/ifund/main/home")
        await self.page.get_by_role("dialog").click()
        await self.page.get_by_role("button", name="รับทราบ").click()

    async def login(self, username: str, password: str) -> None:

        await self.page.get_by_role("button", name="เข้าสู่ระบบ").click()
        await self.page.get_by_role("textbox", name="ชื่อผู้ใช้งาน").click()
        await self.page.get_by_role("textbox", name="ชื่อผู้ใช้งาน").fill(username)
        await self.page.get_by_role("textbox", name="รหัสผ่าน").click()
        await self.page.get_by_role("textbox", name="รหัสผ่าน").fill(password)
        await self.page.get_by_role("dialog").get_by_role("button", name="เข้าสู่ระบบ").click()
        await self.page.wait_for_timeout(5000)
        await self.page.locator("#digit1").click()
        print('digit1 clicked')
        await self.page.wait_for_timeout(15000)

    async def navigate_to_myinvestments(self) -> None:
        await self.page.get_by_role("link", name="การลงทุนของฉัน").click()
        print('Navigated to My Investments')
        await self.page.wait_for_timeout(8000)


    async def get_fund_data(self, fund_name: str) -> None:
        await self.page.get_by_role("textbox", name="ค้นหากองทุนที่คุณต้องการ").click()
        await self.page.get_by_role("textbox", name="ค้นหากองทุนที่คุณต้องการ").press_sequentially(fund_name,delay=100)
        await self.page.wait_for_timeout(800) #wait dropdown list appear

        await self.page.locator("#main-nav-search").get_by_text(fund_name, exact=True).click()
        await self.page.locator("a").filter(has_text="NAV ย้อนหลัง").click()
        await self.page.wait_for_timeout(800) #need wait time to click "ทั้งหมด" otherwise it to fast
        #click select period to download
        await self.page.get_by_role("button", name="ทั้งหมด").click()
        await self.page.wait_for_timeout(800) #need wait time to click "ทั้งหมด" otherwise it to fast
        #click download
        async with self.page.expect_download() as download_info:
            await self.page.get_by_role("link").filter(has_text=re.compile(r"^$")).nth(2).click()
        download = await download_info.value
        savefilename = fund_name + '.csv'
        ifund_file_name = os.path.join(self.download_folder, savefilename)
        await download.save_as(ifund_file_name)
        await self.page.wait_for_timeout(2000)
       


    async def close(self) -> None:
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()


async def run(playwright: Playwright) -> None:
    robot = ifundrobot(playwright)
    await robot.open_main_page()
    #await robot.login("rittxxxx", "xxxxxx")
    #await robot.navigate_to_myinvestments()

    #loop fund list with extract and get data
    for fund in fundlist:
        print(f'Getting data for {fund}')
        await robot.get_fund_data(fund)
        

    await robot.close()


async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)

######################################################
# Class convert raw ifund csv to amibroker csv format#
######################################################

class Convert_raw_ifund_to_amibroker:
    def __init__(self, input_dir, output_dir):
        """
        Initialize the processor with source and destination directories.
        """
        self.input_folder = os.path.expanduser(input_dir)
        self.output_folder = os.path.expanduser(output_dir)
        self._ensure_output_exists()

    def _ensure_output_exists(self):
        """Private method to create output directory if it doesn't exist."""
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
            print(f"Created directory: {self.output_folder}")

    def _process_single_file(self, file_path):
        """Private method to handle the logic for an individual CSV file."""
        file_name = os.path.basename(file_path)
        symbol_name = 'ifund_' + os.path.splitext(file_name)[0]
        
        print(f"Processing: {file_name}...")

        try:
            # Read the raw data file
            df = pd.read_csv(file_path)

            # 2. Logic for Date conversion (dd/mm/yyyy -> yyyy-mm-dd)
            df['Date'] = pd.to_datetime(df['วันที่'], format='%d/%m/%Y', errors='coerce').dt.strftime('%Y-%m-%d')

            # 3. Logic for NAV, sellprice, buyprice, and volume
            # Clean AUM by removing commas before converting to numeric
            df['NAV'] = pd.to_numeric(df['NAV'], errors='coerce')
            df['ราคาขาย'] = pd.to_numeric(df['ราคาขาย'], errors='coerce')
            df['ราคาซื้อคืน'] = pd.to_numeric(df['ราคาซื้อคืน'], errors='coerce')
            df['AUM'] = pd.to_numeric(df['AUM'].astype(str).str.replace(",", ""), errors='coerce')

            # 4. Apply conditional logic for sellprice and buyprice
            # If sellprice/buyprice is NaN (from '-' or Null), set to NAV
            df['sellprice'] = df['ราคาขาย'].fillna(df['NAV'])
            df['buyprice'] = df['ราคาซื้อคืน'].fillna(df['NAV'])

            # 5. Construct the new DataFrame with required columns
            new_df = pd.DataFrame({
                'Date': df['Date'],
                'Tiker': symbol_name,
                'Open': df['NAV'],
                'High': df['sellprice'],
                'Low': df['buyprice'],
                'Close': df['NAV'], # Note: Changed to NAV per your updated logic
                'Volume': df['AUM'],
                'Adj Close': df['NAV']
            })

            # 6. Save the new CSV file to the output folder
            output_file_path = os.path.join(self.output_folder, f"{symbol_name}.csv")
            new_df.to_csv(output_file_path, index=False)
            print(f"Successfully saved: {output_file_path}")
            return True

        except Exception as e:
            print(f"Error processing {file_name}: {e}")
            return False

    def run(self):
        """Main execution method to find and process all files in the input folder."""
        file_pattern = os.path.join(self.input_folder, "*.csv")
        csv_files = glob.glob(file_pattern)

        if not csv_files:
            print(f"No CSV files found in {self.input_folder}")
            return

        success_count = 0
        for file_path in csv_files:
            if self._process_single_file(file_path):
                success_count += 1
        
        print(f"\nProcessing complete. Successfully processed {success_count}/{len(csv_files)} files.")




if __name__ == "__main__":
    ## Define the list of fund names to be processed 
    fundlist = ['ASP-DIGIBLOCRMF','UCI','LHSEMICON-A','ES-CASH','SCBKEQTG','KFGTECHRMF','B-INDIAMRMF',
        'TBIOTECH','SCBNK225','B-EUPASSIVE','B-US2000P','SCBGOLD','ES-OIL','SCBBANKINGA','KT-CHINABOND-A']
    
    ifund_savefolder = str(Path.home() / "Amibroker Data/ifund/ifund_raw")
    convert_file_savefolder = str(Path.home() / "Amibroker Data/Raw Data")

    print("Start download from web ifund \n.")
    asyncio.run(main())
    print("All fund data downloaded successfully \n.")

    ifund_converter = Convert_raw_ifund_to_amibroker(ifund_savefolder, convert_file_savefolder)
    ifund_converter.run()

