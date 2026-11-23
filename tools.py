"""
tools.py - Collection of external tools for CreatorOps AI Agent
Engine: Google News RSS (Reliable, No API Key, No ISP Block)
"""
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

# Setup Logger
logger = logging.getLogger("CreatorOps.Tools")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def search_web(query: str, max_results: int = 5, lang: str = "id") -> List[Dict[str, str]]:
    """
    Melakukan pencarian tren berita via Google News RSS.
    
    Args:
        query (str): Kata kunci pencarian (misal: "AI trend", "Tips Content Creator").
        max_results (int): Jumlah hasil pencarian maksimal.
        lang (str): 'id' untuk Indonesia, 'en' untuk Global.
        
    Returns:
        List[Dict[str, str]]: List of dict berisi 'title', 'link', dan 'snippet'.
    """
    logger.info(f"🔍 [Tool: WebSearch] Executing query: '{query}'")
    
    # Format URL sesuai bahasa
    encoded_query = urllib.parse.quote(query)
    if lang == "id":
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=id&gl=ID&ceid=ID:id"
    else:
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
    try:
        # Pura-pura jadi browser biar gak diblokir header-nya
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        req = urllib.request.Request(rss_url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')[:max_results]
        
        if not items:
            logger.warning("🔍 [Tool: WebSearch] No results found on Google News.")
            return []
            
        clean_results = []
        for item in items:
            title = item.find('title').text if item.find('title') is not None else 'No Title'
            link = item.find('link').text if item.find('link') is not None else ''
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
            
            clean_results.append({
                "title": title,
                "link": link,
                "snippet": f"Published Date: {pub_date}"
            })
            
        logger.info(f"✅ [Tool: WebSearch] Successfully retrieved {len(clean_results)} trend results.")
        return clean_results

    except Exception as e:
        logger.error(f"❌ [Tool: WebSearch] Error searching Google News: {str(e)}")
        return []


def format_search_results_for_llm(results: List[Dict[str, str]]) -> str:
    """
    Helper untuk mengonversi hasil search jadi format teks 
    yang rapi dan siap dikonsumsi oleh LLM.
    """
    if not results:
        return "Tidak ada hasil pencarian yang ditemukan."
    
    formatted_text = "--- HASIL RISET TREN WEB TERKINI ---\n"
    for idx, item in enumerate(results, start=1):
        formatted_text += f"\n[{idx}] {item['title']}\n"
        formatted_text += f"Link: {item['link']}\n"
        formatted_text += f"Info: {item['snippet']}\n"
    formatted_text += "\n-----------------------------------"
    return formatted_text


# --- TEST RUNNER (ISOLATED TEST) ---
if __name__ == "__main__":
    print("🧪 Testing Google News Search Tool...")
    test_query = "Teknologi Artificial Intelligence"
    
    raw_results = search_web(query=test_query, max_results=3, lang="id")
    
    print("\n--- FORMATTED FOR LLM ---")
    print(format_search_results_for_llm(raw_results))