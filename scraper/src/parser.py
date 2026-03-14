from bs4 import BeautifulSoup
import re

def extract_dates(text):
    """Attempt to extract important dates like deadlines."""
    date_patterns = [
        r"(?i)(?:deadline|last date|closing date|apply by)[\s\:\-]+(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",
        r"(?i)(?:deadline|last date|closing date|apply by)[\s\:\-]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"
    ]
    dates = []
    for pattern in date_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            dates.append(match.group(1))
    return list(set(dates)) if dates else None

def extract_eligibility(text):
    """Heuristic extraction of eligibility criteria block."""
    try:
        # Search for eligibility keywords and grab following text chunk
        match = re.search(r'(?i)(?:eligibility|who can apply)[\s\S]{0,50}?(?:criteria|conditions)?[\:\-\s]+([\s\S]{50,500}?)(?=[A-Z][a-z]+[\s]+[A-Z][a-z]+[\:\-]|\Z|\n\n)', text)
        if match:
            # Clean up the output string
            eligibility_str = re.sub(r'\s+', ' ', match.group(1)).strip()
            return eligibility_str
    except Exception:
        pass
    return None

def extract_income(text):
    """Extract income-related criteria."""
    try:
        match = re.search(r'(?i)(?:family|annual)?\s*income.*?((?:rs|inr|₹)?\s*[\d\,\.]+\s*(?:lakhs?|lpa|pa|k|thousands?))', text)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return None

def extract_demographics(text):
    """Extract target demographics (caste, religion, gender)."""
    demographics = []
    text_lower = text.lower()
    
    # Castes / Categories
    if re.search(r'\b(sc|st|obc|ebc|general|minority)\b', text_lower):
        matches = re.finditer(r'\b(sc|st|obc|ebc|general|minority)\b', text_lower)
        demographics.extend(list(set([m.group(1).upper() for m in matches])))
        
    # Gender
    if 'girl' in text_lower or 'female' in text_lower or 'women' in text_lower:
        demographics.append("Female")
    if 'boy' in text_lower or 'male' in text_lower:
        demographics.append("Male")
        
    # Religion
    religions = ['muslim', 'christian', 'sikh', 'buddhist', 'parsi', 'jain', 'hindu']
    for rel in religions:
        if rel in text_lower:
            demographics.append(rel.capitalize())
            
    return list(set(demographics)) if demographics else None

def extract_education(text):
    """Extract target education levels."""
    levels = []
    text_lower = text.lower()
    if re.search(r'\b(class \d{1,2}|\d{1,2}th|school|matric|post-matric)\b', text_lower):
        levels.append("School")
    if re.search(r'\b(ug|undergraduate|bachelor|btech|b\.tech|b\.sc|b\.a|b\.com|degree)\b', text_lower):
        levels.append("Undergraduate")
    if re.search(r'\b(pg|postgraduate|master|mtech|m\.tech|m\.sc|m\.a|m\.com|mca|mba)\b', text_lower):
        levels.append("Postgraduate")
    if re.search(r'\b(phd|ph\.d|research|doctorate)\b', text_lower):
        levels.append("PhD/Research")
        
    return list(set(levels)) if levels else None

def parse_html(html, url):
    """
    Parse the HTML content to extract structured scholarship data.
    """
    if not html:
        return None
        
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = soup.title.string.strip() if soup.title else "No Title"
        
        # Find application links
        apply_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            link_text = a.get_text().lower()
            if 'apply' in link_text or 'register' in link_text or 'click here' in link_text:
                if href.startswith('http'):
                    apply_links.append(href)
                elif href.startswith('/'):
                    base = '/'.join(url.split('/')[:3])
                    apply_links.append(base + href)
        
        apply_links = list(set(apply_links))[:5] # Keep top 5 unique links
        
        # Clean structural cruft to get text
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        
        if len(text) < 150:
            return None
            
        # Extract features
        important_dates = extract_dates(text)
        eligibility = extract_eligibility(text)
        income_limit = extract_income(text)
        demographics = extract_demographics(text)
        education_levels = extract_education(text)
            
        return {
            "url": url,
            "title": title,
            "description_snippet": text[:800] + "..." if len(text) > 800 else text,
            "eligibility_criteria": eligibility,
            "income_limit": income_limit,
            "target_demographics": demographics,
            "education_levels": education_levels,
            "important_dates": important_dates,
            "application_links": apply_links if apply_links else [url],
            "full_text_hash": hash(text)
        }
    except Exception as e:
        print(f"[!] Error parsing HTML for {url}: {e}")
        return None
