$path = "d:\工作文档\学习\SteamWeeklyReports\archive\2026_01_W3_Steam_Dashboard.html"
$lines = Get-Content $path -Encoding UTF8
$newLines = @()
$fixed = $false
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq '// If API fails, keep dropdown usable for "latest"') {
        $newLines += "                console.warn('GitHub API failed, using fallback list:', e);"
        $newLines += "                if (hintEl) hintEl.textContent = '（提示）历史版本列表加载失败，已切换至离线索引。';"
        $newLines += "                archives = ["
        $newLines += "                    { name: '2026_01_W4_Steam_Dashboard.html' },"
        $newLines += "                    { name: '2026_01_W3_Steam_Dashboard.html' }"
        $newLines += "                ];"
        $i++ 
        $fixed = $true
    } else {
        $newLines += $lines[$i]
    }
}
$newLines | Set-Content $path -Encoding UTF8
if ($fixed) { Write-Host "Fixed W3." } else { Write-Host "Target line not found in W3." }
