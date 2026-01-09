from sec_edgar_downloader import Downloader
from pathlib import Path
import os
from dotenv import load_dotenv
def download_10k(ticker:str, num_filing:int = 3):
    load_dotenv()
    email = os.getenv("SEC_USER_EMAIL","you@example.com")
    company_name = os.getenv("SEC_COMPANY_NAME","DemoCompany")
    print(f"Using email: {email} and company name: {company_name} for downloading SEC filings.")
    # Check if Path Exits or Not If Not Create
    path_to_save = "data/raw"
    path = Path(path_to_save)

    path.mkdir(parents=True, exist_ok=True)
    dl = Downloader(email,company_name,path_to_save)
    print("Starting download of 10-K filings")
    dl.get("10-K",ticker,limit=num_filing)

if __name__ == "__main__":
    download_10k(ticker="NVDA",num_filing=2)