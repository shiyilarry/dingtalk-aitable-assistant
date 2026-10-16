# -*- coding: utf-8 -*-
"""
钉钉登录态获取 v3 —— 判定标准收紧为「钉钉登录 cookie 存在」+「当前在看板页」
用法：python login_dingtalk.py      # 弹出窗口 → 在该窗口内扫码（最长等 5 分钟）
产出：.dt_profile/（持久化 profile，后续 headless 直接复用）+ dingtalk_state.json
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
OUT = Path.home() / ".workbuddy" / "dingtalk_state.json"
PROFILE = Path.home() / ".workbuddy" / ".dt_login_profile"
URL = "https://alidocs.dingtalk.com"  # 登录域首页即可（判定=URL 回 alidocs 且非 login/oauth）
AUTH_KEYS = {"sid", "account", "cookie2", "_tb_token_", "sgcookie", "t", "unb", "uc1", "uc3", "lw"}


def snap(ctx, page):
    names = {c["name"].lower() for c in ctx.cookies()}
    hit = sorted(names & AUTH_KEYS)
    u = (page.url or "").lower()
    on_dash = ("alidocs.dingtalk.com" in u) and ("login" not in u) and ("oauth" not in u)
    return hit, on_dash, u


with sync_playwright() as pw:
    print("[login] 启动浏览器新窗口 —— 请在该窗口里扫码登录钉钉（最长等 5 分钟）")
    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE), channel="chrome", headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    try:
        page.goto(URL, wait_until="load", timeout=120000)
    except Exception as e:
        print("[warn] goto:", str(e)[:120])

    ok, hit = False, []
    for i in range(100):                     # 100 × 3s = 300s
        page.wait_for_timeout(3000)
        hit, on_dash, u = snap(ctx, page)
        if i % 4 == 0:
            print("  %3ds | 登录cookie=%s | 看板页=%s | %s" % (i * 3, hit or "无", on_dash, u[:70]))
        if hit and on_dash:
            ok = True
            break

    if ok:
        page.wait_for_timeout(8000)          # 等看板渲染
        ctx.storage_state(path=str(OUT))
        print("[OK] 登录成功！登录cookie:", hit)
        print("[OK] 登录态已导出 ->", OUT)
        sh = BASE / "shots" / "login_ok.png"; sh.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(sh), full_page=True)
        print("[OK] 已截图 ->", sh)
    else:
        hit, on_dash, u = snap(ctx, page)
        print("[FAIL] 超时仍未见登录。最后状态: cookie=%s 看板页=%s url=%s" % (hit or "无", on_dash, u[:120]))
    ctx.close()
