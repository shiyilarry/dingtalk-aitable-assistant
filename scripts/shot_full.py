# -*- coding: utf-8 -*-
"""高视口全屏截图（EV-202610-07 · 1680×2400 一屏全量渲染）

用法: python shot_full.py <dashboardId> <prefix>
说明: 替代滚动分段方案（mouse.wheel 命中不了看板滚动容器，实测不可靠）；
      高视口使全部组件同屏渲染（规避视口外组件被卸载的惰性渲染），一次性 full_page 截全。
      复用 dashboard_session 的登录态（~/.workbuddy/dingtalk_state.json）与清理函数。
边界: ① 内容特别长（>视口高）时仍需分段；② 登录态过期时截图落登录页——如命中请先跑 login_dingtalk.py 重登。
"""
import sys
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

from playwright.sync_api import sync_playwright
import dashboard_session as ds

if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(2)

dash = sys.argv[1]
prefix = sys.argv[2]
SHOTS = ds.SHOTS
STATE = ds.STATE
ANTI = ["--disable-blink-features=AutomationControlled"]

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome", headless=True, args=ANTI)
    ctx = browser.new_context(storage_state=str(STATE), viewport={"width": 1680, "height": 2400})
    page = ctx.new_page()
    page.goto(ds.url_of(dash), wait_until="load", timeout=90000)
    page.wait_for_timeout(12000)
    ds.clean_all(page, rounds=3)
    ds.fold_nav(page)
    page.wait_for_timeout(1200)
    ds.hide_sidebar(page)
    page.wait_for_timeout(2000)
    ds.clean_all(page, rounds=2)
    page.wait_for_timeout(2500)
    out = SHOTS / ("%s_full_hi.png" % prefix)
    page.screenshot(path=str(out), full_page=True)
    print("saved", out)
    ctx.close()
    browser.close()
print("done")
