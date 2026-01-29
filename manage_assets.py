import os
import re
import requests
import time

# 配置
BASE_DIR = r"d:\工作文档\学习\SteamWeeklyReports"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")

# 伪装 Header 防止被拦截
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://store.steampowered.com/"
}

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_appids_and_period(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title_match = re.search(r'<title>.*?\((\d{4}-\d{2}\sW\d+)\)</title>', content)
    if title_match:
        period_str = title_match.group(1).replace('-', '_').replace(' ', '_')
    else:
        filename = os.path.basename(file_path)
        if 'W2' in filename: period_str = '2026_01_W2'
        elif 'W3' in filename: period_str = '2026_01_W3'
        elif 'W4' in filename: period_str = '2026_01_W4'
        else: period_str = 'unknown'
        
    appids = set(re.findall(r'appId["\']?\s*:\s*["\']?(\d+)["\']?', content))
    dom_appids = set(re.findall(r'data-appid=["\'](\d+)["\']', content))
    all_appids = appids.union(dom_appids)
    
    return period_str, all_appids

def download_image(appid, save_path):
    if os.path.exists(save_path):
        if os.path.getsize(save_path) > 0:
            print(f"  [跳过] 已存在: {appid}")
            return
        else:
            print(f"  [警告] 文件为空，重新下载: {appid}")
            os.remove(save_path)

    # 候选 URL 列表 (优先级从高到低)
    # 增加 localized header 支持
    base_akamai = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}"
    base_cloudflare = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}"
    
    candidates = [
        f"{base_akamai}/header.jpg",
        f"{base_akamai}/header_schinese.jpg", # 中文头图
        f"{base_akamai}/header_english.jpg",  # 英文头图
        f"{base_cloudflare}/header.jpg",
        f"{base_akamai}/capsule_616x353.jpg",
        f"{base_akamai}/capsule_616x353_schinese.jpg",
        f"{base_akamai}/library_600x900.jpg"
    ]

    for url in candidates:
        try:
            # print(f"  [尝试] {url} ...") 
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(resp.content)
                print(f"  [成功] 已保存 ({os.path.basename(url)})")
                return 
        except Exception:
            pass
        time.sleep(0.05)
    
    print(f"  [放弃] 所有镜像均失败: {appid}")

def process_file(file_path):
    print(f"\n处理文件: {os.path.basename(file_path)}")
    period, appids = extract_appids_and_period(file_path)
    print(f"  > 识别周期: {period}")
    
    target_dir = os.path.join(ASSETS_DIR, period)
    ensure_dir(target_dir)
    
    for appid in appids:
        save_path = os.path.join(target_dir, f"{appid}.jpg")
        download_image(appid, save_path)

def main():
    ensure_dir(ASSETS_DIR)
    if os.path.exists(INDEX_FILE):
        process_file(INDEX_FILE)
    if os.path.exists(ARCHIVE_DIR):
        for file in os.listdir(ARCHIVE_DIR):
            if file.endswith(".html"):
                process_file(os.path.join(ARCHIVE_DIR, file))

if __name__ == "__main__":
    main()
