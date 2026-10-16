# -*- coding: utf-8 -*-
"""
dashboard_session.py —— 钉钉看板「无人值守会话」工具（SKILL 核心资产）
================================================================
解决三件此前必须人工介入的事（2026-09-10 实证）：
  ① 打开盘页 = 建立 UI 会话窗口        → 无需用户打开/停留
  ② reload 续窗 = 每窗可写 ~5 笔       → 无需用户刷新（实测：刷新后连写 5/5）
  ③ 截图 + 回传                        → 无需用户截图

姿势来源：复用「采集项目」已验证的 Playwright 用法
  pw.chromium.launch(channel="chrome", headless=True, args=["--disable-blink-features=AutomationControlled"])
  browser.new_context(storage_state="dingtalk_state.json")
关键点：
  · 必须 channel="chrome"（用系统 Chrome；agent-browser 在本机启动卡死，勿用）
  · 必须带 --disable-blink-features=AutomationControlled（否则钉钉跳登录页）
  · 登录态用 storage_state（`.dt_profile` 持久化 profile 在钉钉侧无效）
  · headless=True 静默；窗口不弹出、不抢鼠标

用法（先设环境变量 DWS_BASE_ID=<你的 base id>）：
  python dashboard_session.py shot <dashboardId> <前缀>          # 截图
  python dashboard_session.py write <dashboardId> <ops.json>     # 批量写入（自动续窗）
ops.json 格式：[{"chartId":"xxx","config":{...}}, ...]
"""
import json, os, shutil, subprocess, sys, io, time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
STATE = Path.home() / ".workbuddy" / "dingtalk_state.json"
SHOTS = BASE / "shots"; SHOTS.mkdir(exist_ok=True)
# —— 运行时发现（禁硬编码本机路径：跨机/开源通用；找不到则在调用时报明确错误）——
def _first(*ps):
    for p in ps:
        if p and Path(p).exists():
            return str(p)
    return None

NODE = _first(shutil.which("node"),
              r"C:\Program Files\nodejs\node.exe",
              r"D:\Program Files (x86)\nodejs\node.exe")
_dws_js = []
if NODE:
    _p = Path(NODE).parent
    _dws_js += [str(_p / "node-global" / "node_modules" / "dingtalk-workspace-cli" / "bin" / "dws.js"),
                str(_p / "node_modules" / "dingtalk-workspace-cli" / "bin" / "dws.js")]
_dws_js.append(r"D:\Program Files (x86)\nodejs\node-global\node_modules\dingtalk-workspace-cli\bin\dws.js")
DWS = _first(*_dws_js)
BASE_ID = os.environ.get("DWS_BASE_ID", "").strip()   # 运行前设置；不再硬编码

def _preflight():
    if not NODE or not DWS:
        raise SystemExit("未找到 node / dws：请安装 Node.js，并 npm i -g dingtalk-workspace-cli")
    if not BASE_ID:
        raise SystemExit("缺少 base ID：请先设置环境变量 DWS_BASE_ID（如 set DWS_BASE_ID=xxxx）")
ANTI = ["--disable-blink-features=AutomationControlled"]
PER_WINDOW = 4          # 每个会话窗口写几笔后 reload 续窗（实测 5/5 稳、4 更保险）
DISMISS = ["跳过", "下一步", "我知道了", "知道了"]


def dws(args):
    _preflight()
    r = subprocess.run([NODE, DWS, "aitable"] + list(args),
                       capture_output=True, encoding="utf-8", errors="replace")
    o = (r.stdout or "") + (r.stderr or "")
    i, j = o.find("{"), o.rfind("}")
    try:
        return json.loads(o[i:j + 1])
    except Exception:
        return {"_raw": o[:250]}


def url_of(dash_id):
    _preflight()
    return ("https://alidocs.dingtalk.com/i/nodes/%s?entrance=data&applicationId=%s" % (BASE_ID, dash_id))


class DashSession:
    """打开看板页并保持；提供 reload 续窗、批量写入、截图。"""

    def __init__(self, dash_id, headless=True):
        self.dash_id = dash_id
        self.headless = headless
        self.pw = None; self.browser = None; self.ctx = None; self.page = None

    def __enter__(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(channel="chrome", headless=self.headless, args=ANTI)
        self.ctx = self.browser.new_context(storage_state=str(STATE),
                                           viewport={"width": 1680, "height": 1050})
        self.page = self.ctx.new_page()
        self.page.goto(url_of(self.dash_id), wait_until="load", timeout=90000)
        self.page.wait_for_timeout(9000)
        return self

    def __exit__(self, *a):
        try: self.ctx.close()
        except Exception: pass
        try: self.browser.close()
        except Exception: pass
        try: self.pw.stop()
        except Exception: pass

    def reload(self, wait=9000):
        """刷新页面 = 续开一个 UI 会话窗口"""
        self.page.reload(wait_until="load")
        self.page.wait_for_timeout(wait)

    def dismiss(self):
        for t in DISMISS:
            try:
                el = self.page.locator("text=%s" % t).first
                if el.is_visible(timeout=1000):
                    el.click(timeout=2000); self.page.wait_for_timeout(1200)
            except Exception:
                pass

    def shot(self, prefix, full=True, tidy=True):
        if tidy:                       # 默认出“干净整屏”：清弹窗 + 收左栏 + 隐藏表格边栏
            clean_all(self.page)
            fold_nav(self.page)
            self.page.wait_for_timeout(1500)
            hide_sidebar(self.page)
            self.page.wait_for_timeout(1800)
            clean_all(self.page, rounds=2)
        self.dismiss()
        for _ in range(4):
            self.page.mouse.wheel(0, 1600); self.page.wait_for_timeout(900)
        self.page.mouse.wheel(0, -30000); self.page.wait_for_timeout(2200)
        out = SHOTS / ("%s%s.png" % (prefix, "_full" if full else "_view"))
        self.page.screenshot(path=str(out), full_page=full)
        return out

    def write(self, ops, on_log=print):
        """ops: [{'chartId','config'}] —— 自动分批：每 PER_WINDOW 笔 reload 续窗一次"""
        ok = fail = 0
        for n, op in enumerate(ops):
            if n and n % PER_WINDOW == 0:
                self.reload()
                on_log("  [续窗] reload 后继续（已完成 %d 笔）" % n)
            r = dws(["chart", "update", "--base-id", BASE_ID, "--dashboard-id", self.dash_id,
                     "--chart-id", op["chartId"],
                     "--config", json.dumps(op["config"], ensure_ascii=False), "--format", "json"])
            good = (r.get("data") or {}).get("chartId") or r.get("success")
            if not good:                       # 失败立即续窗重试一次
                self.reload()
                r = dws(["chart", "update", "--base-id", BASE_ID, "--dashboard-id", self.dash_id,
                         "--chart-id", op["chartId"],
                         "--config", json.dumps(op["config"], ensure_ascii=False), "--format", "json"])
                good = (r.get("data") or {}).get("chartId") or r.get("success")
            on_log("  %s %s" % ("OK  " if good else "FAIL", op.get("label") or op["chartId"][:12]))
            ok += bool(good); fail += (not good)
        return ok, fail


# ============ 2026-09-10 新增：通用弹窗清理 + 两条 XPath 定位 ============
XP_NAV_COLLAPSE = ("/html/body/div[1]/div/div/div/div/div[1]/div/div[1]/div[4]/div/div/div[1]"
                   "/div[1]/div[3]/div/div")
XP_HIDE_SIDEBAR = ("/html/body/div[1]/div/div/div/div[2]/div[1]/div/div/div[1]/div[2]/div[1]/div[1]"
                   "/div[1]/div/div/div[2]/div/div/button[2]")

_JS_CLEAN = """() => {
  const out = [];
  for (const e of document.querySelectorAll('div,span,button,a')) {
    const t = (e.textContent||'').trim();
    if (t.length > 14 || !/跳过|我知道了|知道了|关闭/.test(t)) continue;
    const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
    try { e.click(); out.push('txt:' + t); } catch (err) {}
  }
  return out;
}"""

_JS_BIGMODAL = """() => {
  let best = null;
  for (const e of document.querySelectorAll('div')) {
    const r = e.getBoundingClientRect();
    if (r.width < 360 || r.width > 1400 || r.height < 200) continue;
    if (r.left < 20 || r.top < 20) continue;
    const c = (e.className || '').toString();
    if (!/modal|Modal|dialog|Dialog|popup|Popup|mask|guide|Guide|announce/.test(c)) continue;
    if (!best || r.width * r.height > best.w * best.h) best = {x: r.left, y: r.top, w: r.width, h: r.height};
  }
  return best;
}"""


def fold_nav(page, log=print):
    """点「钉钉文档左栏折叠」（宿主页）"""
    for i, f in enumerate(page.frames):
        try:
            loc = f.locator("xpath=%s" % XP_NAV_COLLAPSE)
            if loc.count():
                loc.first.click(timeout=6000, force=True)
                log("    [左栏折叠] frame[%d] 已点击" % i); return True
        except Exception:
            pass
    log("    [左栏折叠] 未找到"); return False


def hide_sidebar(page, log=print):
    """点「AI 表格隐藏边栏」（notable iframe）"""
    for i, f in enumerate(page.frames):
        try:
            loc = f.locator("xpath=%s" % XP_HIDE_SIDEBAR)
            if loc.count():
                loc.first.click(timeout=6000, force=True)
                log("    [隐藏边栏] frame[%d] 已点击" % i); return True
        except Exception:
            pass
    log("    [隐藏边栏] 未找到"); return False


def clean_all(page, rounds=5, log=print):
    """清理所有遮挡弹窗：文本按钮 → Escape → 大弹窗自锚右上角关闭"""
    for i in range(rounds):
        hits = []
        for f in page.frames:
            try:
                hits += (f.evaluate(_JS_CLEAN) or [])
            except Exception:
                pass
        page.keyboard.press("Escape")
        page.wait_for_timeout(500)
        box = None
        for f in page.frames:
            try:
                box = f.evaluate(_JS_BIGMODAL)
            except Exception:
                box = None
            if box:
                break
        if box:
            page.mouse.click(box["x"] + box["w"] - 20, box["y"] + 22)
            hits.append("corner:%.0fx%.0f" % (box["w"], box["h"]))
        page.wait_for_timeout(900)
        if not hits:
            log("    [弹窗] 第 %d 轮后已清理干净" % (i + 1)); return
        log("    [弹窗] 第 %d 轮: %s" % (i + 1, hits))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "shot":
        dash, prefix = sys.argv[2], sys.argv[3]
        with DashSession(dash) as s:
            p = s.shot(prefix)
            print("saved:", p)
    elif cmd == "write":
        dash, opsfile = sys.argv[2], sys.argv[3]
        ops = json.loads(Path(opsfile).read_text(encoding="utf-8"))
        with DashSession(dash) as s:
            ok, fail = s.write(ops)
            print("写入结果: OK %d / FAIL %d" % (ok, fail))
            p = s.shot("after_write")
            print("saved:", p)
    else:
        print(__doc__)
