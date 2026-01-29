import os
import base64
import re

BASE_DIR = r"d:\工作文档\学习\SteamWeeklyReports"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ARCHIVE_DIR = os.path.join(BASE_DIR, "archive")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")

def image_to_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_html(file_path):
    print(f"Processing {os.path.basename(file_path)}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Identify Period
    title_match = re.search(r'<title>.*?\((\d{4}-\d{2}\sW\d+)\)</title>', content)
    if title_match:
        period = title_match.group(1).replace('-', '_').replace(' ', '_')
    else:
        # Fallback based on filename
        if 'W2' in file_path: period = '2026_01_W2'
        elif 'W3' in file_path: period = '2026_01_W3'
        elif 'W4' in file_path: period = '2026_01_W4'
        else: 
            print("  -> Cannot identify period, skipping.")
            return

    print(f"  -> Period: {period}")
    
    # 2. Find all AppIDs in the file
    appids = set(re.findall(r'appId["\']?\s*:\s*["\']?(\d+)["\']?', content))
    dom_appids = set(re.findall(r'data-appid=["\'](\d+)["\']', content))
    all_appids = appids.union(dom_appids)
    
    # 3. Generate Base64 Map
    b64_map = {}
    assets_path = os.path.join(ASSETS_DIR, period)
    
    for appid in all_appids:
        img_path = os.path.join(assets_path, f"{appid}.jpg")
        b64 = image_to_base64(img_path)
        if b64:
            b64_map[appid] = f"data:image/jpeg;base64,{b64}"
            print(f"  -> Embedded {appid} ({len(b64)//1024} KB)")
        else:
            print(f"  -> Missing asset for {appid}")

    # 4. Inject into HTML
    # We will inject a script block before the main script that defines 'embeddedImages'
    # and modify 'steamImageCandidates' to use it.
    
    # Construct the JS object string
    js_obj_str = "const embeddedImages = {\n"
    for appid, data in b64_map.items():
        js_obj_str += f'            "{appid}": "{data}",\n'
    js_obj_str += "        };\n"

    # Check if we already injected it
    if "const embeddedImages =" in content:
        # Replace existing block
        content = re.sub(r'const embeddedImages = \{[\s\S]*?\};', js_obj_str.strip(), content)
    else:
        # Insert at the beginning of the script tag
        content = content.replace('<script>', f'<script>\n        {js_obj_str}')

    # 5. Modify steamImageCandidates to prioritize embeddedImages
    new_function = """
        function steamImageCandidates(appId) {
            // 0. Embedded Base64 (Highest Priority)
            if (typeof embeddedImages !== 'undefined' && embeddedImages[appId]) {
                return [embeddedImages[appId]];
            }

            // 1. Local Asset Path (Fallback)
            const isArchive = window.location.pathname.includes('/archive/');
            const prefix = isArchive ? '../assets/' : 'assets/';
            const period = (typeof reportData !== 'undefined' && reportData.periodCode) ? reportData.periodCode : '2026_01_W4';
            const localPath = `${prefix}${period}/${appId}.jpg`;

            // 2. Remote Fallbacks
            const cdn1 = `https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/${appId}`;
            const cdn2 = `https://cdn.cloudflare.steamstatic.com/steam/apps/${appId}`;
            const cdn4 = `https://steamcdn-a.akamaihd.net/steam/apps/${appId}`;
            const ts = `?t=${new Date().getTime()}`;

            return [
                localPath,
                `${cdn1}/header.jpg${ts}`, 
                `${cdn1}/header_schinese.jpg${ts}`,
                `${cdn2}/header.jpg${ts}`,
                `${cdn1}/library_600x900.jpg${ts}`,
                `${cdn1}/capsule_184x69.jpg${ts}`
            ];
        }
    """
    
    # Replace the existing function using regex to handle variations
    content = re.sub(r'function steamImageCandidates\(appId\) \{[\s\S]*?^\s*\}', new_function.strip(), content, flags=re.MULTILINE)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  -> Saved.")

def main():
    # Process Index
    if os.path.exists(INDEX_FILE):
        process_html(INDEX_FILE)
    
    # Process Archives
    if os.path.exists(ARCHIVE_DIR):
        for file in os.listdir(ARCHIVE_DIR):
            if file.endswith(".html"):
                process_html(os.path.join(ARCHIVE_DIR, file))

if __name__ == "__main__":
    main()
