# -*- coding: utf-8 -*-
"""
看板无头预检（复用采集项目已验证的 Playwright 姿势 + 持久化登录态）
能力：静默打开看板 → 关引导弹窗 → 滚动触发渲染 → 整页截图 → 回传供 AI 读图
用法：python shot_dashboard.py <url> [前缀]
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
SHOTS = BASE / "shots"; SHOTS.mkdir(exist_ok=True)
PROFILE = BASE / ".dt_profile"          # 首次用 login_dingtalk.py 登录后长期复用

url = sys.argv[1] if len(sys.argv) > 1 else None
prefix = sys.argv[2] if len(sys.argv) > 2 else "shot"
if not url:
    print("usage: python shot_dashboard.py <url> [prefix]"); sys.exit(2)

DISMISS = ["跳过", "下一步", "我知道了", "知道了", "关闭", "不再提示"]

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE), channel="chrome", headless=True,
        viewport={"width": 1680, "height": 1050})
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    try:
        page.goto(url, wait_until="load", timeout=90000)
    except Exception as e:
        print("[warn] goto:", str(e)[:150])
    page.wait_for_timeout(9000)

    # 关掉引导/教学弹窗（逐个尝试，找不到就跳过）
    for t in DISMISS:
        try:
            el = page.locator("text=%s" % t).first
            if el.is_visible(timeout=1200):
                el.click(timeout=2500)
                print("[dismiss] 已点击:", t)
                page.wait_for_timeout(1500)
        except Exception:
            pass
    try:                                  # 兜底：ESC 关弹层
        page.keyboard.press("Escape"); page.wait_for_timeout(800)
    except Exception:
        pass

    # 滚动触发懒加载后回顶
    for _ in range(4):
        page.mouse.wheel(0, 1600); page.wait_for_timeout(1000)
    page.mouse.wheel(0, -30000); page.wait_for_timeout(2500)

    full = SHOTS / ("%s_full.png" % prefix)
    page.screenshot(path=str(full), full_page=True)
    view = SHOTS / ("%s_view.png" % prefix)
    page.screenshot(path=str(view), full_page=False)
    print("title:", page.title())
    print("url  :", page.url[:110])
    print("saved:", full)
    print("saved:", view)
    ctx.close()
