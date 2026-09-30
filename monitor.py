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
    # =========================
    # 佳佳唱片
    # =========================
    {
        "id": "ccr_paranoid",
        "shop": "佳佳唱片",
        "album": "偏执面",
        "url": "https://www.ccr.com.tw/goods/462721",
        "type": "ccr",
    },
    {
        "id": "ccr_story",
        "shop": "佳佳唱片",
        "album": "偷故事的人",
        "url": "https://www.ccr.com.tw/goods/462722",
        "type": "ccr",
    },
    {
        "id": "ccr_amit2",
        "shop": "佳佳唱片",
        "album": "AMIT 2",
        "url": "https://www.ccr.com.tw/goods/462720",
        "type": "ccr",
    },

    # =========================
    # 环球 Fangoods
    # =========================
    {
        "id": "fangoods_paranoid",
        "shop": "环球 Fangoods",
        "album": "偏执面",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?ItemId=10248",
        "type": "fangoods",
    },
    {
        "id": "fangoods_story",
        "shop": "环球 Fangoods",
        "album": "偷故事的人",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?ItemId=10291",
        "type": "fangoods",
    },
    {
        "id": "fangoods_amit2",
        "shop": "环球 Fangoods",
        "album": "AMIT 2",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?ItemId=10249",
        "type": "fangoods",
    },

    # =========================
    # 五大唱片
    # =========================
    {
        "id": "5music_paranoid",
        "shop": "五大唱片",
        "album": "偏执面",
        "url": "https://www.5music.com.tw/CDList-C.asp?cdno=438475678968",
        "type": "5music",
    },
    {
        "id": "5music_story",
        "shop": "五大唱片",
        "album": "偷故事的人",
        "url": "https://www.5music.com.tw/CDList-C.asp?cdno=439405678604",
        "type": "5music",
    },
    {
        "id": "5music_amit2",
        "shop": "五大唱片",
        "album": "AMIT 2",
        "url": "https://www.5music.com.tw/CDList-C.asp?cdno=438475678969",
        "type": "5music",
    },

    # =========================
    # 滚石 ROCKMALL
    # =========================
    {
        "id": "rockmall_paranoid",
        "shop": "滚石 ROCKMALL",
        "album": "偏执面",
        "url": "https://shop.rockmall.com.tw/product_view.php?id=100083",
        "type": "rockmall",
    },
    {
        "id": "rockmall_story",
        "shop": "滚石 ROCKMALL",
        "album": "偷故事的人",
        "url": "https://shop.rockmall.com.tw/product_view.php?id=100084",
        "type": "rockmall",
    },
    {
        "id": "rockmall_amit2",
        "shop": "滚石 ROCKMALL",
        "album": "AMIT 2",
        "url": "https://shop.rockmall.com.tw/product_view.php?id=100082",
        "type": "rockmall",
    },

    # =========================
    # 诚品
    # =========================
    {
        "id": "eslite_paranoid",
        "shop": "诚品线上",
        "album": "偏执面",
        "url": "https://www.eslite.com/product/1004123082633742",
        "type": "eslite",
    },
    {
        "id": "eslite_story",
        "shop": "诚品线上",
        "album": "偷故事的人",
        "url": "https://www.eslite.com/product/1004123082662038",
        "type": "eslite",
    },
    {
        "id": "eslite_amit2",
        "shop": "诚品线上",
        "album": "AMIT 2",
        "url": "https://www.eslite.com/product/1004123082633743",
        "type": "eslite",
    },

    # =========================
    # 九五乐府：首页监控三张
    # =========================
    {
        "id": "95_paranoid",
        "shop": "九五乐府",
        "album": "偏执面",
        "url": "https://www.95music.com/",
        "type": "line",
        "needle": "偏執面",
    },
    {
        "id": "95_story",
        "shop": "九五乐府",
        "album": "偷故事的人",
        "url": "https://www.95music.com/",
        "type": "line",
        "needle": "偷故事的人",
    },
    {
        "id": "95_amit2",
        "shop": "九五乐府",
        "album": "AMIT 2",
        "url": "https://www.95music.com/",
        "type": "line",
        "needle": "阿密特2",
    },

    # =========================
    # 山海山：张惠妹商品列表
    # =========================
    {
        "id": "shs_paranoid",
        "shop": "山海山唱片",
        "album": "偏执面",
        "url": "https://www.shsmusic.tw/tw/product/index.php?artist=2203&sort=4",
        "type": "line",
        "needle": "偏執面",
    },
    {
        "id": "shs_story",
        "shop": "山海山唱片",
        "album": "偷故事的人",
        "url": "https://www.shsmusic.tw/tw/product/index.php?artist=2203&sort=4",
        "type": "line",
        "needle": "偷故事的人",
    },
    {
        "id": "shs_amit2",
        "shop": "山海山唱片",
        "album": "AMIT 2",
        "url": "https://www.shsmusic.tw/tw/product/index.php?artist=2203&sort=4",
        "type": "line",
        "needle": "阿密特2",
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

    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()

    for enc in ("utf-8", "big5", "cp950"):
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
    source = re.sub(
        r"</(div|p|li|tr|td|h1|h2|h3|h4|h5|h6)>",
        "\n",
        source,
        flags=re.I,
    )

    source = re.sub(r"<[^>]+>", " ", source)
    source = html.unescape(source)
    source = source.replace("\u3000", " ")

    source = re.sub(r"[ \t]+", " ", source)
    source = re.sub(r"\n+", "\n", source)

    return source.strip()


def first(pattern, text, default=""):
    m = re.search(pattern, text, flags=re.I | re.S)
    if not m:
        return default

    return re.sub(r"\s+", " ", m.group(1)).strip()


def parse_ccr(text):
    price = first(
        r"網路價\s*NT\$\s*[:：]?\s*([\d,]+)",
        text,
    )

    release = first(
        r"發行日期\s*[:：]?\s*(20\d{2}/\d{2}/\d{2})",
        text,
    )

    if "無庫存" in text:
        stock = "无库存"
        available = False

    elif "加入購物車" in text or "現貨" in text:
        stock = "可购买"
        available = True

    else:
        stock = "状态待确认"
        available = False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "note": release,
    }


def parse_fangoods(text):
    stock_num = first(
        r"庫存量\s*[:：]?\s*(\d+)",
        text,
    )

    price = first(
        r"價\s*格\s*[:：]?\s*\$?\s*([\d,]+)",
        text,
    )

    shipping = first(
        r"出貨時間\s*[:：]?\s*([^\n]+)",
        text,
    )

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
        "note": shipping[:50],
    }


def parse_5music(text):
    ship = first(
        r"出貨日期\s*[:：]?\s*([^\n]+)",
        text,
    )

    price = first(
        r"特價\s*\$?\s*([\d,]+)",
        text,
    )

    if "目前無現貨" in text:
        stock = "目前无现货"
        available = False

    elif "放入購物車" in text or "ADD To cart" in text:
        stock = "可加入购物车"
        available = True

    else:
        stock = "状态待确认"
        available = False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "note": ship,
    }


def parse_rockmall(text):
    price = first(
        r"定價\s*[:：]?\s*([\d,]+)",
        text,
    )

    release = first(
        r"預定發行[〗】]?\s*(20\d{2}[./]\d{1,2}[./]\d{1,2}[^\n]*)",
        text,
    )

    if "售完" in text:
        stock = "售完"
        available = False

    elif "加入購物車" in text or "立即購買" in text:
        stock = "可购买"
        available = True

    else:
        stock = "状态待确认"
        available = False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "note": release,
    }


def parse_eslite(text):
    note = ""

    for key in [
        "再版預購中",
        "再版預購完銷",
        "到倉後出貨",
        "貨到通知",
        "無法購買",
    ]:
        if key in text:
            note += key + " "

    if (
        "貨到通知" in text
        or "無法購買" in text
        or "已絕版" in text
    ):
        stock = "暂不可购买"
        available = False

    elif "加入購物車" in text or "立即購買" in text:
        stock = "可购买"
        available = True

    else:
        stock = "状态待确认"
        available = False

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": note.strip(),
    }


def parse_line(text, needle):
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    matches = [
        line
        for line in lines
        if needle.lower() in line.lower()
    ]

    if not matches:
        return {
            "stock": "页面暂未找到该专辑",
            "available": False,
            "price": "",
            "note": "",
        }

    line = matches[0]

    negative = [
        "無庫存",
        "无库存",
        "售完",
        "完銷",
        "绝版",
        "絕版",
    ]

    positive = [
        "有現貨",
        "现货",
        "有庫存",
        "加入購物車",
        "可購買",
    ]

    if any(word in line for word in negative):
        available = False
        stock = "暂不可购买"

    elif any(word in line for word in positive):
        available = True
        stock = "可能可购买"

    else:
        available = False
        stock = "已上架，状态待确认"

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": line[:220],
    }


def check_item(item):
    source = fetch(item["url"])
    text = visible_text(source)

    if item["type"] == "ccr":
        result = parse_ccr(text)

    elif item["type"] == "fangoods":
        result = parse_fangoods(text)

    elif item["type"] == "5music":
        result = parse_5music(text)

    elif item["type"] == "rockmall":
        result = parse_rockmall(text)

    elif item["type"] == "eslite":
        result = parse_eslite(text)

    elif item["type"] == "line":
        result = parse_line(
            text,
            item["needle"],
        )

    else:
        raise ValueError("Unknown parser type")

    result["checked_at"] = now_text()

    return result


def telegram_send(message):
    endpoint = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    data = urllib.parse.urlencode(
        {
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        endpoint,
        data=data,
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=20,
    ) as response:
        response.read()


def load_state():
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(
            STATE_FILE.read_text(
                encoding="utf-8",
            )
        )

    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(
        json.dumps(
            state,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def comparable(status):
    return {
        key: value
        for key, value in status.items()
        if key != "checked_at"
    }


def format_message(item, old, new):
    if (
        new.get("available")
        and not old.get("available")
    ):
        title = "🚨 到货 / 恢复购买"

    else:
        title = "🔔 专辑状态变化"

    lines = [
        title,
        "",
        f"专辑：{item['album']}",
        f"平台：{item['shop']}",
        f"原状态：{old.get('stock', '未知')}",
        f"最新状态：{new.get('stock', '未知')}",
    ]

    if new.get("price"):
        lines.append(
            f"价格：{new['price']}"
        )

    if new.get("note"):
        lines.append(
            f"页面信息：{new['note']}"
        )

    lines.extend(
        [
            f"发现时间：{new['checked_at']}",
            item["url"],
        ]
    )

    return "\n".join(lines)


def main():
    old_state = load_state()
    new_state = {}

    newly_added = []

    for item in WATCHES:
        try:
            status = check_item(item)
            new_state[item["id"]] = status

            old = old_state.get(
                item["id"]
            )

            if old is None:
                newly_added.append(
                    (
                        item,
                        status,
                    )
                )
                continue

            if (
                comparable(old)
                != comparable(status)
            ):
                telegram_send(
                    format_message(
                        item,
                        old,
                        status,
                    )
                )

        except Exception as exc:
            print(
                f"ERROR "
                f"{item['id']}: "
                f"{exc}"
            )

            if item["id"] in old_state:
                new_state[item["id"]] = (
                    old_state[item["id"]]
                )

    save_state(new_state)

    if newly_added:
        lines = [
            "✅ 新监控渠道已接入",
            "",
        ]

        for item, status in newly_added:
            lines.append(
                f"{item['shop']}｜"
                f"{item['album']}："
                f"{status.get('stock', '未知')}"
            )

        lines.extend(
            [
                "",
                "以后这些渠道只有状态变化时才提醒。",
                f"更新时间：{now_text()}",
            ]
        )

        telegram_send(
            "\n".join(lines)
        )


if __name__ == "__main__":
    main()
