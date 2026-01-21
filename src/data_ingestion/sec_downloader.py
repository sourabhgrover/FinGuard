from sec_edgar_downloader import Downloader
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import List,Dict
from datetime import datetime
import json
import time

def download_10k(ticker:str, num_filing:int = 3):
    load_dotenv()
    email = os.getenv("SEC_USER_EMAIL","you@example.com")
    company_name = os.getenv("SEC_COMPANY_NAME","DemoCompany")
    # Check if Path Exits or Not If Not Create
    path_to_save = "data/raw"
    path = Path(path_to_save)

    try:
        path.mkdir(parents=True, exist_ok=True)
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
    
def download_multiple_10k(tickers : List[str],num_filing:int) -> Dict[str,List[Path]]:
    print("Downloading multiple 10k...")
    all_fillings = {}
    for i,ticker in enumerate(tickers,1):
       print(f"\n[{i}/{len(tickers)}] Processing {ticker}...")
       result = download_10k(ticker=ticker,num_filing=num_filing)
       all_fillings.update(result)
       
       if i < len(tickers):
            print("Waiting for 1 seconds before next download to respect SEC rate limits...")
            time.sleep(1)  # Sleep for 1 second between downloads to respect SEC rate limits   
    return all_fillings

def get_download_summary() -> Dict[str,any]:
    print("Creating download summary")
    path_to_save = "data/raw"
    path = Path(path_to_save)
    metadata_files = list(path.glob("*_download_metadata.json"))
    summary = {
        "total_ticker_attempted" : len(metadata_files),
        "successfull_downloads": 0,
        "failed_downloads": 0,
        "total_files": 0,
        "details": []
    }

    for metadata_file in metadata_files:
        with open(metadata_file,'r',encoding="utf-8") as f:
            metadata = json.load(f)
            if metadata.get("download_status") == "success":
                summary["successfull_downloads"] +=1
                summary["total_files"] += metadata.get("num_filing",0)
            else:
                summary["failed_downloads"] +=1
            
            summary["details"].append(metadata)

    return summary


if __name__ == "__main__":
    result = download_multiple_10k(["AAPL","NVDA","INVALID_TICKER_XYZ"],num_filing=3)

    print("\n"+ "="*60)
    print("Download Summary:")
    summary = get_download_summary()
    print(json.dumps(summary,indent=2))