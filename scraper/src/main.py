import time
from search import find_scholarship_urls
from downloader import download_page
from parser import parse_html
from storage import save_data

def run_crawler():
    print("=== Scholarship Crawler: Phase 1 ===")
    
    queries = [
        # Broad categories
        "all active scholarships for indian students",
        "merit cum means scholarships india",
        "low income family scholarships india",
        
        # Demographics & Religion
        "scholarships for minority students muslim christian sikh india",
        "scholarships for SC ST OBC EBC students in india",
        "scholarships for girls female students in india",
        
        # Academic Levels
        "scholarships for class 10 12 school students india",
        "undergraduate btech bsc degree scholarships india",
        "postgraduate mtech mca master scholarships india",
        "phd research fellowships scholarships india",
        
        # University/State specific
        "state government scholarships for college students",
        "central government scholarships for university students india",
        
        # Top platforms
        "site:buddy4study.com scholarships",
        "site:scholarships.gov.in active schemes",
        "site:vidyasaarathi.co.in scholarships"
    ]
    
    target_results_per_query = 8
    all_extracted_data = []
    
    for query in queries:
        print(f"\n--- Processing Query: '{query}' ---")
        urls = find_scholarship_urls(query, num_results=target_results_per_query)
        print(f"[*] Found {len(urls)} URLs.")
        
        for url in urls:
            print(f"\n[*] Downloading: {url}")
            html = download_page(url)
            
            if html:
                print(f"[*] Parsing data...")
                parsed_data = parse_html(html, url)
                
                if parsed_data:
                    all_extracted_data.append(parsed_data)
                    safe_title = parsed_data['title'].encode('ascii', 'ignore').decode('ascii')
                    print(f"[+] Successfully extracted data. Title: '{safe_title}'")
                else:
                    print("[-] No useful data extracted.")
            
            # Be polite to servers by sleeping lightly between downloads
            time.sleep(1)
            
    print("\n=== Crawl Summary ===")
    print(f"Total pages successfully processed: {len(all_extracted_data)}")
    
    # Save the aggregated results (stored in the src directory where script runs)
    if all_extracted_data:
        save_data(all_extracted_data, "scholarships_data.json")
    else:
        print("[-] No data collected during this run.")

if __name__ == "__main__":
    run_crawler()
