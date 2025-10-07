# # main.py
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests

# app = Flask(__name__)
# CORS(app)

# @app.route("/generate", methods=["POST"])
# def generate():
#     data = request.json
#     command = data.get("command")  # <-- match frontend
#     if not command:
#         return jsonify({"error": "No command provided"}), 400

#     try:
#         # Call Ollama API
#         res = requests.post(
#             "http://127.0.0.1:11434/api/generate",
#             json={"model": "llama3:latest", "prompt": command, "stream": False},
#         )
#         res.raise_for_status()
#         output = res.json()
#         return jsonify({"response": output.get("response", "No response from Ollama")})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)

# backend/main.py


# -----------------------------------------------------------


# from flask import Flask, request, jsonify, send_file
# from flask_cors import CORS
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import unquote, urlparse, parse_qs
# from playwright.sync_api import sync_playwright
# import os

# app = Flask(__name__)
# CORS(app)

# SCREENSHOT_DIR = "screenshots"
# os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# # --- DuckDuckGo search with real URLs ---
# def search_duckduckgo(query, limit=5):
#     url = f"https://duckduckgo.com/html/?q={query}"
#     headers = {"User-Agent": "Mozilla/5.0"}
#     r = requests.get(url, headers=headers, timeout=10)
#     soup = BeautifulSoup(r.text, "html.parser")

#     results = []
#     for a in soup.select(".result__a")[:limit]:
#         title = a.get_text(strip=True)
#         href = a["href"]
        
#         # Extract the real URL from uddg parameter
#         parsed = urlparse(href)
#         qs = parse_qs(parsed.query)
#         real_url = unquote(qs.get("uddg", [href])[0])
#         results.append({"title": title, "link": real_url})
#     return results

# # --- Fetch page content and screenshot ---
# def fetch_page_content_and_screenshot(url, idx):
#     result = {"content": "Failed to load page.", "screenshot": None}
#     try:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             context = browser.new_context(
#                 user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
#             )
#             page = context.new_page()
#             page.goto(url, timeout=20000)  # 20s timeout
#             page.wait_for_load_state("networkidle", timeout=15000)

#             # Screenshot
#             screenshot_path = os.path.join(SCREENSHOT_DIR, f"screenshot_{idx}.png")
#             page.screenshot(path=screenshot_path, full_page=True)

#             # Extract text content (first 500 chars)
#             text_content = page.inner_text("body")[:500]
#             result["content"] = text_content
#             result["screenshot"] = screenshot_path

#             browser.close()
#     except Exception as e:
#         # keep fallback message in result['content']
#         result["content"] = f"Failed to load page: {str(e)}"
#     return result

# # --- API endpoint ---
# @app.route("/execute", methods=["POST"])
# def execute():
#     data = request.json
#     command = data.get("command", "").strip()

#     if not command:
#         return jsonify({"results": [], "error": "No command provided"})

#     try:
#         results = search_duckduckgo(command, limit=5)
#         enhanced_results = []
#         for idx, res in enumerate(results):
#             extra = fetch_page_content_and_screenshot(res["link"], idx)
#             enhanced_results.append({
#                 "title": res["title"],
#                 "link": res["link"],
#                 "content": extra["content"],
#                 "screenshot": extra["screenshot"]
#             })
#         return jsonify({"results": enhanced_results})
#     except Exception as e:
#         return jsonify({"results": [], "error": str(e)})

# # --- Serve screenshots ---
# @app.route("/screenshot/<filename>")
# def get_screenshot(filename):
#     path = os.path.join(SCREENSHOT_DIR, filename)
#     if os.path.exists(path):
#         return send_file(path, mimetype="image/png")
#     return "Not found", 404

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse, parse_qs
from playwright.sync_api import sync_playwright
from PIL import Image
import os
import time
import hashlib

app = Flask(__name__)
CORS(app)

SCREENSHOT_DIR = "screenshots"
THUMBNAIL_DIR = "thumbnails"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(THUMBNAIL_DIR, exist_ok=True)

# --- Enhanced DuckDuckGo search ---
def search_duckduckgo(query, limit=5):
    """Enhanced DuckDuckGo search with better error handling"""
    try:
        url = f"https://duckduckgo.com/html/?q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        
        # Try multiple selectors for better compatibility
        result_selectors = [".result__a", ".result .result__title a", "a[href*='uddg']"]
        
        for selector in result_selectors:
            links = soup.select(selector)
            if links:
                break
        
        for i, a in enumerate(links[:limit]):
            if not a:
                continue
                
            title = a.get_text(strip=True)
            if not title:
                title = f"Result {i+1}"
                
            href = a.get("href", "")
            if not href:
                continue
                
            # Extract real URL from DuckDuckGo redirect
            try:
                parsed = urlparse(href)
                qs = parse_qs(parsed.query)
                real_url = unquote(qs.get("uddg", [href])[0])
                
                # Validate URL
                if not real_url.startswith(("http://", "https://")):
                    real_url = "https://" + real_url.lstrip("/")
                    
                results.append({
                    "title": title,
                    "link": real_url,
                    "category": categorize_result(title, real_url)
                })
            except Exception as e:
                print(f"Error processing URL {href}: {e}")
                continue
                
        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

def categorize_result(title, url):
    """Categorize search results based on title and URL"""
    title_lower = title.lower()
    url_lower = url.lower()
    
    # Gaming keywords
    if any(word in title_lower for word in ['game', 'gaming', 'steam', 'xbox', 'playstation', 'nintendo']):
        return 'gaming'
    
    # Tech keywords
    if any(word in title_lower for word in ['tech', 'technology', 'software', 'hardware', 'computer', 'laptop', 'mobile', 'ai', 'artificial intelligence']):
        return 'tech'
    
    # Business keywords
    if any(word in title_lower for word in ['business', 'finance', 'market', 'company', 'corporate', 'startup', 'investment']):
        return 'business'
    
    # News keywords
    if any(word in url_lower for word in ['news', 'bbc', 'cnn', 'reuters', 'times']):
        return 'news'
    
    return 'general'

# --- Create thumbnail ---
def create_thumbnail(screenshot_path, idx, width=300):
    """Create thumbnail from screenshot with error handling"""
    thumbnail_filename = f"thumb_{idx}_{int(time.time())}.png"
    thumbnail_path = os.path.join(THUMBNAIL_DIR, thumbnail_filename)
    
    try:
        if not os.path.exists(screenshot_path):
            return None
            
        with Image.open(screenshot_path) as img:
            # Calculate height maintaining aspect ratio
            aspect_ratio = img.height / img.width
            height = int(width * aspect_ratio)
            
            # Resize image
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
            img_resized.save(thumbnail_path, "PNG", optimize=True)
            
        return thumbnail_path
    except Exception as e:
        print(f"Thumbnail creation error: {e}")
        return None

# --- Enhanced page content and screenshot fetching ---
def fetch_page_content_and_screenshot(url, idx):
    """Enhanced page fetching with better error handling and content extraction"""
    result = {
        "content": "Failed to load page.",
        "screenshot": None,
        "thumbnail": None,
        "status": "error"
    }
    
    try:
        # Create unique filenames
        timestamp = int(time.time())
        screenshot_filename = f"screenshot_{idx}_{timestamp}.png"
        screenshot_path = os.path.join(SCREENSHOT_DIR, screenshot_filename)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080}
            )
            
            page = context.new_page()
            
            # Set timeouts
            page.set_default_timeout(30000)
            
            # Navigate to page
            response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
            
            if not response or response.status >= 400:
                result["content"] = f"Page returned status {response.status if response else 'unknown'}"
                browser.close()
                return result
            
            # Wait for page to load
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                # If networkidle fails, just wait a bit
                page.wait_for_timeout(3000)
            
            # Take screenshot
            try:
                page.screenshot(
                    path=screenshot_path,
                    full_page=True,
                    type="png"
                )
                result["screenshot"] = screenshot_path
                
                # Create thumbnail
                thumbnail_path = create_thumbnail(screenshot_path, idx)
                if thumbnail_path:
                    result["thumbnail"] = thumbnail_path
                    
            except Exception as e:
                print(f"Screenshot error for {url}: {e}")
            
            # Extract content
            try:
                # Remove script and style elements
                page.evaluate("""
                    () => {
                        const scripts = document.querySelectorAll('script, style, noscript');
                        scripts.forEach(el => el.remove());
                    }
                """)
                
                # Get main content
                content_selectors = [
                    "main", "article", ".main-content", ".content", 
                    "#main", "#content", ".post-content", ".entry-content"
                ]
                
                content_text = ""
                for selector in content_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            content_text = element.inner_text()
                            break
                    except:
                        continue
                
                # Fallback to body if no main content found
                if not content_text:
                    try:
                        content_text = page.query_selector("body").inner_text()
                    except:
                        content_text = ""
                
                # Clean and truncate content
                if content_text:
                    lines = [line.strip() for line in content_text.split('\n') if line.strip()]
                    clean_lines = [line for line in lines if len(line) > 10]  # Remove very short lines
                    content_text = ' '.join(clean_lines[:15])  # First 15 meaningful lines
                    
                    if len(content_text) > 500:
                        content_text = content_text[:500] + "..."
                    
                    result["content"] = content_text if content_text else "No content extracted."
                    result["status"] = "success"
                else:
                    result["content"] = "No readable content found."
                    
            except Exception as e:
                result["content"] = f"Content extraction failed: {str(e)}"
                print(f"Content extraction error for {url}: {e}")
            
            browser.close()
            
    except Exception as e:
        result["content"] = f"Failed to load page: {str(e)}"
        print(f"Page fetch error for {url}: {e}")
    
    return result

# --- Main API endpoint ---
@app.route("/execute", methods=["POST"])
def execute():
    """Enhanced API endpoint with better error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"results": [], "error": "No JSON data provided"})
        
        command = data.get("command", "").strip()
        if not command:
            return jsonify({"results": [], "error": "No search query provided"})
        
        print(f"Processing search query: {command}")
        
        # Search DuckDuckGo
        search_results = search_duckduckgo(command, limit=6)  # Get a few extra in case some fail
        
        if not search_results:
            return jsonify({
                "results": [],
                "error": "No search results found. Please try a different query."
            })
        
        print(f"Found {len(search_results)} search results")
        
        # Process each result
        enhanced_results = []
        for idx, result in enumerate(search_results[:5]):  # Limit to 5 final results
            print(f"Processing result {idx+1}: {result['title'][:50]}...")
            
            try:
                # Fetch page content and screenshot
                page_data = fetch_page_content_and_screenshot(result["link"], idx)
                
                enhanced_result = {
                    "title": result["title"],
                    "link": result["link"],
                    "content": page_data["content"],
                    "screenshot": page_data["screenshot"],
                    "thumbnail": page_data["thumbnail"],
                    "category": result.get("category", "general"),
                    "status": page_data.get("status", "error")
                }
                
                enhanced_results.append(enhanced_result)
                
            except Exception as e:
                print(f"Error processing result {idx}: {e}")
                # Add result even if processing failed
                enhanced_results.append({
                    "title": result["title"],
                    "link": result["link"],
                    "content": f"Failed to process: {str(e)}",
                    "screenshot": None,
                    "thumbnail": None,
                    "category": result.get("category", "general"),
                    "status": "error"
                })
        
        print(f"Returning {len(enhanced_results)} processed results")
        
        return jsonify({
            "results": enhanced_results,
            "query": command,
            "total_found": len(enhanced_results)
        })
        
    except Exception as e:
        print(f"API error: {e}")
        return jsonify({
            "results": [],
            "error": f"Server error: {str(e)}"
        }), 500

# --- Serve screenshots ---
@app.route("/screenshot/<filename>")
def get_screenshot(filename):
    """Serve screenshot files"""
    try:
        path = os.path.join(SCREENSHOT_DIR, filename)
        if os.path.exists(path):
            return send_file(path, mimetype="image/png")
        return "Screenshot not found", 404
    except Exception as e:
        print(f"Screenshot serve error: {e}")
        return "Error serving screenshot", 500

# --- Serve thumbnails ---
@app.route("/thumbnail/<filename>")
def get_thumbnail(filename):
    """Serve thumbnail files"""
    try:
        path = os.path.join(THUMBNAIL_DIR, filename)
        if os.path.exists(path):
            return send_file(path, mimetype="image/png")
        return "Thumbnail not found", 404
    except Exception as e:
        print(f"Thumbnail serve error: {e}")
        return "Error serving thumbnail", 500

# --- Health check endpoint ---
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Web Navigator API is running",
        "timestamp": time.time()
    })

# --- Clean up old files (optional) ---
def cleanup_old_files():
    """Clean up old screenshot and thumbnail files"""
    try:
        current_time = time.time()
        for directory in [SCREENSHOT_DIR, THUMBNAIL_DIR]:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    file_age = current_time - os.path.getctime(filepath)
                    # Remove files older than 1 hour
                    if file_age > 3600:
                        os.remove(filepath)
                        print(f"Cleaned up old file: {filename}")
    except Exception as e:
        print(f"Cleanup error: {e}")

if __name__ == "__main__":
    print("Starting Web Navigator AI Agent Backend...")
    print("Server will be available at: http://127.0.0.1:5000")
    print("Make sure to install dependencies: pip install flask flask-cors requests beautifulsoup4 playwright pillow")
    print("Also run: playwright install chromium")
    
    # Optional: Clean up old files on startup
    cleanup_old_files()
    
    app.run(
        host="127.0.0.1", 
        port=5000, 
        debug=True,
        threaded=True
    )