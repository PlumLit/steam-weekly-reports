import os
import requests

BASE_DIR = r"d:\工作文档\学习\SteamWeeklyReports\assets"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://store.steampowered.com/"
}

# 手动获取的顽固 URL 映射
MANUAL_URLS = {
    "2026_01_W4": {
        "3543120": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3543120/21854e6cc5a4fe8d23dbc7c49be8bc364e6e65df/header_schinese.jpg",
        "3840050": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3840050/30459dcda259681fc6200b36f07e573ede893dbb/header.jpg",
        "2956680": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2956680/ec69f31952fce97b7bed794f3fdd3f1640ef228f/header_schinese.jpg",
        "4038930": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/4038930/715ad2df014ff002e0ea973e8a174bd3e8ec0a93/header_schinese.jpg"
    },
    "2026_01_W2": {
        "3639650": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3639650/63f508087d52472b52cd3cbd48ade5f9cb01210e/header_schinese.jpg",
        "2797960": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2797960/3813fdc68d06bb465e4246d77a643ad35368796b/header_schinese.jpg",
        "3880360": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3880360/0861a5b153fd6faced0ce860e0530719330c53e7/header.jpg",
        "3850560": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3850560/8b64c53cbb4fb3af13704d3e9c62b5660e3c2f64/header_schinese.jpg"
    },
    "2026_01_W3": {
        "3679930": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3679930/c59f5e58993c6a4827028c23143b8dd928399727/header_schinese.jpg",
        "3707400": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3707400/1f6ec1822a33ba9d4872ef4f5d2b04c0b7df1fc4/header_schinese.jpg",
        "3764490": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3764490/b7cf286123555a3c98fd8b2de6554433c2e2a1c7/header.jpg",
        "2529000": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2529000/d4923278e81fece8c30c6589e3e3f4b386c5a25f/header_schinese.jpg",
        "3942480": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3942480/41e25fa0325879aceff8f2d6b2b39d6c3017cf25/header_schinese.jpg",
        "3543320": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/3543320/8461ee0769ae04ac3c86566a4c0e02628cea1950/header.jpg"
    }
}

def download():
    for period, items in MANUAL_URLS.items():
        folder = os.path.join(BASE_DIR, period)
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        for appid, url in items.items():
            save_path = os.path.join(folder, f"{appid}.jpg")
            if os.path.exists(save_path) and os.path.getsize(save_path) > 0:
                print(f"Skipping {appid} (exists)")
                continue
                
            print(f"Downloading {appid} from {url}...")
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                if resp.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(resp.content)
                else:
                    print(f"Failed {appid}: {resp.status_code}")
            except Exception as e:
                print(f"Error {appid}: {e}")

if __name__ == "__main__":
    download()
