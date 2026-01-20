from sec_edgar_downloader import Downloader
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import List
from datetime import datetime
import json

def download_10k(ticker:str, num_filing:int = 3):
    load_dotenv()
    email = os.getenv("SEC_USER_EMAIL","you@example.com")
    company_name = os.getenv("SEC_COMPANY_NAME","DemoCompany")
    # Check if Path Exits or Not If Not Create
    path_to_save = "data/raw"
    path = Path(path_to_save)

    try:
        path.mkdir(parents=True, exist_ok=True)

        # Force exception for testing
        # if test_exception:
        #     raise Exception("Simulated error for testing")
        dl = Downloader(email,company_name,path_to_save)
        print(f"Starting download {ticker} of 10-K filings")
        dl.get("10-K",ticker,limit=num_filing)
        
        ticker_path = path / "sec-edgar-filings" / ticker / "10-K"
        filing_paths = []

        if ticker_path.exists():
            for filing_dir in sorted(ticker_path.iterdir())[-num_filing:]:
                txt_file = filing_dir / "full-submission.txt"
                if txt_file.exists():
                    filing_paths.append(txt_file)
                    print(f" Found: {filing_dir.name}")

        # Save download metadata for audit trail     
        metadata = {
            "ticker" : ticker,
            "download_date": datetime.now().isoformat(),
            "num_filing" : len(filing_paths),
            "file_paths" : [str(p) for p in filing_paths],
            "download_status": "success" if filing_paths else "no_files_found"
        }
        metadata_path = path / f"{ticker}_download_metadata.json"

        with open(metadata_path,"w",encoding="utf-8") as f:
            json.dump(metadata,f,indent=2)

        print(f"Successfully downloaded {len(filing_paths)} filing for {ticker}")
        return {ticker : filing_paths}

    except Exception as e:
        print(f"Error downloading filings for {ticker}: {str(e)}")

        error_metadata ={
            "ticker": ticker,
            "download_data": datetime.now().isoformat(),
            "error": str(e),
            "download_status": "failed"
        }

        metadata_path = path / f"{ticker}_download_metadata.json"
        with open(metadata_path,"w",encoding='utf-8') as f:
            json.dump(error_metadata,f,indent=2)

        return {ticker:[]}
    
def download_multiple_10k(tickers : List[str],num_filing:int):
    print("Download multiple 10k")
    for ticker in tickers:
        download_10k(ticker=ticker,num_filing=num_filing)
    return

if __name__ == "__main__":
    download_multiple_10k(["AAPL","NVDA","INVALID_TICKER_XYZ"],num_filing=3)