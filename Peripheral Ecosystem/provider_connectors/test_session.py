import os
import requests
from auth_session_provider import ChartinkAuthSessionProvider

def test_chartink_authentication():
    print("=== Chartink Session Authentication Test ===")
    
    # 1. Initialize auth provider
    auth_provider = ChartinkAuthSessionProvider()
    cookies = auth_provider.load_session_cookies()
    
    if not cookies:
        print("❌ [FAILED] No cookies found or file is empty at:")
        print(f"    {auth_provider.session_file}")
        return

    print(f"✅ Loaded {len(cookies)} cookie(s) from local store.")

    # 2. Setup session with cookies
    session = requests.Session()
    session.cookies.update(cookies)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://chartink.com/screener/"
    }

    # 3. Test request against saved scanner or main screener page
    test_url = "https://chartink.com/screener/copy-ankur-s-breakout-scans-4680"
    print(f"🌐 Testing connection to saved scanner endpoint...")
    
    try:
        response = session.get(test_url, headers=headers, timeout=10)
        print(f"📡 Response Status Code: {response.status_code}")
        print(f"🔗 Final URL: {response.url}")
        
        if response.status_code == 200 and "login" not in response.url.lower():
            print("🎉 SUCCESS: Session is ACTIVE and fully authenticated!")
            
            # Test the process endpoint as well
            process_url = "https://chartink.com/screener/process"
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            token_meta = soup.find("meta", {"name": "csrf-token"})
            if token_meta:
                headers["x-csrf-token"] = token_meta["content"]
                
            post_resp = session.post(process_url, headers=headers, timeout=10)
            print(f"⚙️ Screener Process Endpoint Status: {post_resp.status_code}")
            if post_resp.status_code == 200:
                data = post_resp.json()
                print(f"📊 Live Scan Raw Results Count: {len(data.get('data', [])) if isinstance(data, dict) else 'Unknown'}")
        else:
            print("⚠️ WARNING: Session appears expired or redirected to login. Please re-export your cookies using the Cookie Editor extension.")
            
    except Exception as e:
        print(f"❌ ERROR during network request: {e}")

if __name__ == "__main__":
    test_chartink_authentication()