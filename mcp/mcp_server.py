import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
import json

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

def fetch_ai_news() -> str:
    """
    Secure MCP tool that autonomously fetches the Google News RSS feed for AI,
    extracts the top 5 article titles, and grabs a brief snippet of their content.
    """
    url = "https://news.google.com/rss/search?q=Artificial+Intelligence+when:1d&hl=en-US&gl=US&ceid=US:en"
    try:
        # Standard User-Agent to prevent basic blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the first 5 <item> tags
        items = soup.find_all('item')[:5]
        
        extracted_data = []
        for item in items:
            title = item.title.text if item.title else "No Title"
            
            # html.parser treats <link> as a self-closing tag, so the URL text ends up as the next sibling
            url_link = "#"
            if item.link and item.link.next_sibling:
                url_link = str(item.link.next_sibling).strip()
            
            # The description often contains HTML inside the RSS, we want pure text
            description = item.description.text if item.description else ""
            desc_soup = BeautifulSoup(description, 'html.parser')
            snippet = desc_soup.get_text(strip=True)
            
            if not snippet:
                snippet = "No Description"
            
            # Deep fetch the actual article content for maximum LLM context
            full_text = snippet
            try:
                if url_link != "#":
                    article_resp = requests.get(url_link, headers=headers, timeout=8)
                    article_resp.raise_for_status()
                    article_soup = BeautifulSoup(article_resp.content, 'html.parser')
                    paragraphs = article_soup.find_all('p')
                    p_text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                    if len(p_text) > len(snippet):
                        full_text = p_text[:5000] # Provide up to 5000 chars of deep context per article
            except Exception as e:
                pass # Silent fallback to RSS snippet if scraping fails
                
            extracted_data.append({
                "title": title,
                "url": url_link,
                "snippet": full_text
            })
            
        return json.dumps({
            "status": "success",
            "content": extracted_data
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "content": str(e)
        })
