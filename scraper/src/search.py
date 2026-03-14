from ddgs import DDGS
import time

def find_scholarship_urls(query, num_results=5):
    """
    Search for a given query and return a list of URLs using DuckDuckGo.
    Includes a fallback mechanism if search fails.
    """
    print(f"[*] Searching for: '{query}'")
    urls = []
    try:
        # Using DDG search which doesn't rate limit as aggressively
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=num_results, region='in-en')
            for result in results:
                if 'href' in result and result['href'] not in urls:
                    urls.append(result['href'])
    except Exception as e:
        print(f"[!] Error during search: {e}")
        
    # Fallback to known scholarship resources if search yields few results
    if len(urls) < 2:
        print("[!] Search yielded few results, using fallback URLs.")
        fallback_urls = [
            "https://scholarships.gov.in/",
            "https://www.buddy4study.com/scholarships",
            "https://www.buddy4study.com/article/minority-scholarships",
            "https://www.buddy4study.com/article/post-matric-scholarship-for-sc-students",
            "https://www.aicte-india.org/schemes/students-development-schemes",
            "https://www.ugc.ac.in/page/Scholarships-and-Fellowships.aspx",
            "https://www.vidyasaarathi.co.in/Vidyasaarathi/scholarship",
            "https://www.buddy4study.com/article/scholarships-for-girls",
            "https://www.india.gov.in/topics/education-training/scholarships",
            "https://nsp.gov.in/"
        ]
        # Allow expanding fallback slice based on how many results are requested
        urls.extend(fallback_urls[:max(num_results, len(fallback_urls))])
        
    return urls
