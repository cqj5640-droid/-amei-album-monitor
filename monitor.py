import os
import re
import json
import html
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

STATE_FILE = Path("state.json")

WATCHES = [
    {
        "id": "ccr_paranoid",
        "shop": "佳佳唱片",
        "album": "偏执面",
        "version": "神经白胶唱片（重发版）",
        "url": "https://www.ccr.com.tw/goods/462721",
        "type": "ccr",
    },
    {
        "id": "ccr_story",
        "shop": "佳佳唱片",
        "album": "偷故事的人",
        "version": "黑胶（重发版）",
        "url": "https://www.ccr.com.tw/goods/462722",
        "type": "ccr",
    },
    {
        "id": "ccr_amit2",
        "shop": "佳佳唱片",
        "album": "AMIT 2",
        "version": "视觉黑胶唱片（重发版）",
        "url": "https://www.ccr.com.tw/goods/462720",
        "type": "ccr",
    },

    {
        "id": "fangoods_paranoid",
        "shop": "环球唱片 Fangoods",
        "album": "偏执面",
        "version": "神经白胶唱片",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?Hash=15F82FDAEDF20AF7C958B69CE762B2C4&ItemId=10248&PubK=484649&m=80E3CEC5ACBCD193F672C3247B4575D4BE1D743F00B33C6A",
        "type": "fangoods",
    },
    {
        "id": "fangoods_story",
        "shop": "环球唱片 Fangoods",
        "album": "偷故事的人",
        "version": "黑胶唱片",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?Hash=15F82FDAEDF20AF7C958B69CE762B2C4&ItemId=10291&PubK=484649&m=80E3CEC5ACBCD193F672C3247B4575D4BE1D743F00B33C6A",
        "type": "fangoods",
    },
    {
        "id": "fangoods_amit2",
        "shop": "环球唱片 Fangoods",
        "album": "AMIT 2",
        "version": "视觉黑胶唱片",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?Hash=7AB949DD74D207C1EF159C754E14B345&ItemId=10249&PubK=302717&m=80E3CEC5ACBCD193F672C3247B4575D4BE1D743F00B33C6A",
        "type": "fangoods",
    },
]


def now_text():
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
                "AppleWebKit/605.1.15 Version/18.0 Mobile/15E148 Safari/604.1"
            ),
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read()

    for enc in ["utf-8", "big5", "cp950"]:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass

    return raw.decode("utf-8", errors="ignore")


def visible_text(source):
    source = re.sub(
        r"<(script|style).*?>.*?</\1>",
        " ",
        source,
        flags=re.I | re.S,
    )
    source = re.sub(r"<br\s*/?>", "\n", source, flags=re.I)
    source = re.sub(r"</(div|p|li|tr|td|h\d)>", "\n", source, flags=re.I)
    source = re.sub(r"<[^>]+>", " ", source)
    source = html.unescape(source)
    source = source.replace("\u3000", " ")
    source = re.sub(r"[ \t]+", " ", source)
    source = re.sub(r"\n+", "\n", source)
    return source.strip()


def find_first(pattern, text, default=""):
    m = re.search(pattern, text, flags=re.I | re.S)
    if not m:
        return default
    return re.sub(r"\s+", " ", m.group(1)).strip()


def parse_ccr(text):
    price = find_first(r"網路價\s*NT\$\s*[:：]?\s*([\d,]+)\s*元", text)
    release = find_first(r"發行日期\s*[:：]?\s*(20\d{2}/\d{2}/\d{2})", text)

    if "無庫存" in text:
        stock = "无库存"
        available = False
    elif "現貨" in text or "加入購物車" in text or "購物車" in text:
        stock = "可能可购买"
        available = True
    else:
        stock = "页面未显示“无库存”"
        available = True

    tags = []
    for word in ["預購", "新品", "現貨", "無庫存"]:
        if word in text:
            tags.append(word)

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "release": release,
        "tags": " / ".join(tags),
    }


def parse_fangoods(text):
    stock_num = find_first(r"庫存量\s*[:：]?\s*(\d+)", text)
    price = find_first(r"價\s*格\s*[:：]?\s*\$?\s*([\d,]+)", text)
    release = find_first(r"發行日\s*[:：]?\s*(20\d{2}/\d{2}/\d{2})", text)
    shipping = find_first(r"出貨時間\s*[:：]?\s*([^\n]+)", text)

    if stock_num:
        n = int(stock_num)
        stock = f"库存 {n}"
        available = n > 0
    else:
        stock = "库存数量未识别"
        available = False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "release": release,
        "shipping": shipping[:30] if shipping else "",
    }


def check_item(item):
    source = fetch(item["url"])
    text = visible_text(source)

    if item["type"] == "ccr":
        status = parse_ccr(text)
    else:
        status = parse_fangoods(text)

    status["checked_at"] = now_text()
    return status


def telegram_send(message):
    endpoint = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode(
        {
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    req = urllib.request.Request(endpoint, data=data, method="POST")

    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def comparable(status):
    return {
        k: v
        for k, v in status.items()
        if k != "checked_at"
    }


def format_status(item, status, title):
    lines = [
        title,
        "",
        f"专辑：{item['album']}",
        f"版本：{item['version']}",
        f"店家：{item['shop']}",
        f"状态：{status.get('stock', '')}",
    ]

    if status.get("price"):
        lines.append(f"价格：{status['price']}")

    if status.get("release"):
        lines.append(f"发行日：{status['release']}")

    if status.get("shipping"):
        lines.append(f"出货：{status['shipping']}")

    if status.get("tags"):
        lines.append(f"页面标记：{status['tags']}")

    lines.extend(
        [
            f"检查时间：{status.get('checked_at', now_text())}",
            item["url"],
        ]
    )

    return "\n".join(lines)


def main():
    old_state = load_state()
    new_state = {}

    first_run = not bool(old_state)
    first_run_lines = [
        "✅ A-MEI Album Monitor 已启动",
        "",
        "当前监控：佳佳唱片 + 环球 Fangoods",
        "专辑：《偏执面》《偷故事的人》《AMIT 2》",
        "",
    ]

    for item in WATCHES:
        try:
            status = check_item(item)
            new_state[item["id"]] = status

            old = old_state.get(item["id"])

            if first_run:
                first_run_lines.append(
                    f"{item['shop']}｜{item['album']}："
                    f"{status.get('stock', '未知')}"
                )

            elif old is not None and comparable(old) != comparable(status):
                old_stock = old.get("stock", "未知")
                new_stock = status.get("stock", "未知")

                if status.get("available") and not old.get("available"):
                    title = "🚨 可能到货 / 恢复购买"
                else:
                    title = "🔔 专辑页面状态发生变化"

                msg = (
                    format_status(item, status, title)
                    + f"\n\n上次状态：{old_stock}"
                    + f"\n最新状态：{new_stock}"
                )
                telegram_send(msg)

        except Exception as e:
            new_state[item["id"]] = old_state.get(
                item["id"],
                {
                    "error": str(e)[:200],
                    "checked_at": now_text(),
                },
            )
            print(f"ERROR {item['id']}: {e}")

    save_state(new_state)

    if first_run:
        first_run_lines.extend(
            [
                "",
                "以后只有监控状态发生变化时才会通知。",
                f"初始化时间：{now_text()}",
            ]
        )
        telegram_send("\n".join(first_run_lines))


if __name__ == "__main__":
    main()
