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
    # ==================================================
    # 佳佳唱片
    # ==================================================
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

    # ==================================================
    # 环球 Fangoods
    # 使用完整官方网址，不能只保留 ItemId
    # ==================================================
    {
        "id": "fangoods_paranoid",
        "shop": "环球 Fangoods",
        "album": "偏执面",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?Hash=15F82FDAEDF20AF7C958B69CE762B2C4&ItemId=10248&PubK=484649&m=80E3CEC5ACBCD193F672C3247B4575D4BE1D743F00B33C6A",
        "type": "fangoods",
    },
    {
        "id": "fangoods_story",
        "shop": "环球 Fangoods",
        "album": "偷故事的人",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?Hash=15F82FDAEDF20AF7C958B69CE762B2C4&ItemId=10291&PubK=484649&m=80E3CEC5ACBCD193F672C3247B4575D4BE1D743F00B33C6A",
        "type": "fangoods",
    },
    {
        "id": "fangoods_amit2",
        "shop": "环球 Fangoods",
        "album": "AMIT 2",
        "url": "https://www.fangoods.com.tw/UMG/Default.aspx?Hash=7AB949DD74D207C1EF159C754E14B345&ItemId=10249&PubK=302717&m=80E3CEC5ACBCD193F672C3247B4575D4BE1D743F00B33C6A",
        "type": "fangoods",
    },

    # ==================================================
    # 五大唱片
    # ==================================================
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

    # ==================================================
    # 滚石 ROCKMALL
    # ==================================================
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

    # ==================================================
    # 诚品线上
    # ==================================================
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

    # ==================================================
    # 九五乐府
    # ==================================================
    {
        "id": "95_paranoid",
        "shop": "九五乐府",
        "album": "偏执面",
        "url": "https://www.95music.com/",
        "type": "line",
        "needles": ["偏執面", "偏执面"],
    },
    {
        "id": "95_story",
        "shop": "九五乐府",
        "album": "偷故事的人",
        "url": "https://www.95music.com/",
        "type": "line",
        "needles": ["偷故事的人"],
    },
    {
        "id": "95_amit2",
        "shop": "九五乐府",
        "album": "AMIT 2",
        "url": "https://www.95music.com/",
        "type": "line",
        "needles": ["阿密特2", "阿密特 2", "AMIT 2", "AMIT2"],
    },

    # ==================================================
    # 山海山唱片
    # ==================================================
    {
        "id": "shs_paranoid",
        "shop": "山海山唱片",
        "album": "偏执面",
        "url": "https://www.shsmusic.tw/tw/product/index.php?artist=2203&sort=4",
        "type": "line",
        "needles": ["偏執面", "偏执面"],
    },
    {
        "id": "shs_story",
        "shop": "山海山唱片",
        "album": "偷故事的人",
        "url": "https://www.shsmusic.tw/tw/product/index.php?artist=2203&sort=4",
        "type": "line",
        "needles": ["偷故事的人"],
    },
    {
        "id": "shs_amit2",
        "shop": "山海山唱片",
        "album": "AMIT 2",
        "url": "https://www.shsmusic.tw/tw/product/index.php?artist=2203&sort=4",
        "type": "line",
        "needles": ["阿密特2", "阿密特 2", "AMIT2", "AMIT 2"],
    },
]


def now_text():
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def fetch(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
                "AppleWebKit/605.1.15 Version/18.0 "
                "Mobile/15E148 Safari/604.1"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()

    for encoding in ("utf-8", "big5", "cp950"):
        try:
            return raw.decode(encoding)
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

    source = re.sub(
        r"<br\s*/?>",
        "\n",
        source,
        flags=re.I,
    )

    source = re.sub(
        r"</(div|p|li|tr|td|h1|h2|h3|h4|h5|h6)>",
        "\n",
        source,
        flags=re.I,
    )

    source = re.sub(
        r"<[^>]+>",
        " ",
        source,
    )

    source = html.unescape(source)
    source = source.replace("\u3000", " ")

    source = re.sub(
        r"[ \t]+",
        " ",
        source,
    )

    source = re.sub(
        r"\n+",
        "\n",
        source,
    )

    return source.strip()


def first(pattern, text, default=""):
    match = re.search(
        pattern,
        text,
        flags=re.I | re.S,
    )

    if not match:
        return default

    return re.sub(
        r"\s+",
        " ",
        match.group(1),
    ).strip()


# ==================================================
# 佳佳
# ==================================================

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
        valid = True

    elif "加入購物車" in text or "現貨" in text:
        stock = "可购买"
        available = True
        valid = True

    else:
        stock = "状态暂未识别"
        available = False
        valid = False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "note": release,
        "valid": valid,
    }


# ==================================================
# 环球 Fangoods
# ==================================================

def parse_fangoods(text):
    stock_num = first(
        r"庫存量\s*[:：]?\s*(\d+)",
        text,
    )

    price = first(
        r"價\s*格\s*[:：]?\s*\$?\s*([\d,]+)",
        text,
    )

    release = first(
        r"發行日\s*[:：]?\s*(20\d{2}/\d{2}/\d{2})",
        text,
    )

    shipping = first(
        r"出貨時間\s*[:：]?\s*([^\n]+)",
        text,
    )

    if not stock_num:
        return {
            "stock": "库存数量未识别",
            "available": False,
            "price": f"NT${price}" if price else "",
            "note": "",
            "valid": False,
        }

    number = int(stock_num)

    note_parts = []

    if release:
        note_parts.append(
            f"发行日 {release}"
        )

    if shipping:
        note_parts.append(
            f"出货 {shipping[:40]}"
        )

    return {
        "stock": f"库存 {number}",
        "available": number > 0,
        "price": f"NT${price}" if price else "",
        "note": "；".join(note_parts),
        "valid": True,
    }


# ==================================================
# 五大
# ==================================================

def parse_5music(text):
    price = first(
        r"(?:特價|售價)\s*[:：]?\s*\$?\s*([\d,]+)",
        text,
    )

    shipping = first(
        r"(?:預計)?出貨(?:日期|日)?\s*[:：]?\s*([^\n]+)",
        text,
    )

    if "目前無現貨" in text:
        stock = "目前无现货"
        available = False
        valid = True

    elif (
        "加入購物車" in text
        or "放入購物車" in text
        or "ADD To cart" in text
        or "ADD TO CART" in text
    ):
        stock = "可加入购物车"
        available = True
        valid = True

    else:
        stock = "状态暂未识别"
        available = False
        valid = False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "note": shipping[:80] if shipping else "",
        "valid": valid,
    }


# ==================================================
# 滚石 ROCKMALL
# ==================================================

def parse_rockmall(text):
    price = first(
        r"(?:定價|售價)\s*[:：]?\s*\$?\s*([\d,]+)",
        text,
    )

    release = first(
        r"(20\d{2}[./-]\d{1,2}[./-]\d{1,2}[^\n]*)",
        text,
    )

    if "售完" in text:
        stock = "售完"
        available = False
        valid = True

    elif (
        "加入購物車" in text
        or "立即購買" in text
        or "立即购买" in text
    ):
        stock = "可购买"
        available = True
        valid = True

    else:
        stock = "状态暂未识别"
        available = False
        valid = False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "note": release[:100] if release else "",
        "valid": valid,
    }


# ==================================================
# 诚品
# ==================================================

def parse_eslite(text):
    notes = []

    for key in [
        "再版預購中",
        "再版預購完銷",
        "預購完銷",
        "到倉後出貨",
        "貨到通知",
        "缺貨",
        "暫無庫存",
    ]:
        if key in text:
            notes.append(key)

    if (
        "貨到通知" in text
        or "預購完銷" in text
        or "再版預購完銷" in text
        or "缺貨" in text
        or "暫無庫存" in text
    ):
        stock = "暂不可购买"
        available = False
        valid = True

    elif (
        "加入購物車" in text
        or "立即購買" in text
        or "加入购物车" in text
        or "立即购买" in text
    ):
        stock = "可购买"
        available = True
        valid = True

    elif "再版預購中" in text:
        stock = "预购中"
        available = True
        valid = True

    else:
        stock = "状态暂未识别"
        available = False
        valid = False

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": " / ".join(notes),
        "valid": valid,
    }


# ==================================================
# 九五 / 山海山
# ==================================================

def parse_line(text, needles):
    lines = [
        re.sub(
            r"\s+",
            " ",
            line,
        ).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    matched_line = ""

    for line in lines:
        lower_line = line.lower()

        if any(
            needle.lower() in lower_line
            for needle in needles
        ):
            matched_line = line
            break

    if not matched_line:
        return {
            "stock": "页面暂未找到该专辑",
            "available": False,
            "price": "",
            "note": "",
            "valid": False,
        }

    negative_words = [
        "無庫存",
        "无库存",
        "售完",
        "完銷",
        "预购完销",
        "預購完銷",
        "缺貨",
        "缺货",
    ]

    positive_words = [
        "現貨",
        "现货",
        "有庫存",
        "有库存",
        "加入購物車",
        "加入购物车",
        "可購買",
        "可购买",
    ]

    preorder_words = [
        "預購",
        "预购",
        "第二批",
        "到貨",
        "到货",
    ]

    if any(
        word in matched_line
        for word in negative_words
    ):
        stock = "暂不可购买"
        available = False
        valid = True

    elif any(
        word in matched_line
        for word in positive_words
    ):
        stock = "可能可购买"
        available = True
        valid = True

    elif any(
        word in matched_line
        for word in preorder_words
    ):
        stock = "有预购/到货信息"
        available = False
        valid = True

    else:
        stock = "已上架，库存状态待确认"
        available = False
        valid = True

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": matched_line[:250],
        "valid": valid,
    }


# ==================================================
# 检查单个商品
# ==================================================

def check_item(item):
    source = fetch(
        item["url"]
    )

    text = visible_text(
        source
    )

    item_type = item["type"]

    if item_type == "ccr":
        result = parse_ccr(text)

    elif item_type == "fangoods":
        result = parse_fangoods(text)

    elif item_type == "5music":
        result = parse_5music(text)

    elif item_type == "rockmall":
        result = parse_rockmall(text)

    elif item_type == "eslite":
        result = parse_eslite(text)

    elif item_type == "line":
        result = parse_line(
            text,
            item["needles"],
        )

    else:
        raise ValueError(
            f"Unknown parser: {item_type}"
        )

    result["checked_at"] = now_text()

    return result


# ==================================================
# Telegram
# ==================================================

def telegram_send(message):
    endpoint = (
        f"https://api.telegram.org/"
        f"bot{BOT_TOKEN}/sendMessage"
    )

    body = urllib.parse.urlencode(
        {
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")

    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=20,
    ) as response:
        response.read()


# ==================================================
# 保存状态
# ==================================================

def load_state():
    if not STATE_FILE.exists():
        return {}

    try:
        return json.loads(
            STATE_FILE.read_text(
                encoding="utf-8"
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
        "stock": status.get("stock", ""),
        "available": status.get("available", False),
        "price": status.get("price", ""),
        "note": status.get("note", ""),
    }


# ==================================================
# 通知文字
# ==================================================

def format_message(
    item,
    old,
    new,
):
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


# ==================================================
# 主程序
# ==================================================

def main():
    old_state = load_state()

    new_state = dict(
        old_state
    )

    new_items = []

    for item in WATCHES:
        try:
            status = check_item(
                item
            )

            # 关键防误报：
            # 页面没识别成功时，
            # 不覆盖旧状态，也不发通知。
            if not status.get(
                "valid",
                False,
            ):
                print(
                    "SKIP invalid result:",
                    item["shop"],
                    item["album"],
                    status.get(
                        "stock",
                        "",
                    ),
                )
                continue

            old = old_state.get(
                item["id"]
            )

            new_state[
                item["id"]
            ] = status

            if old is None:
                new_items.append(
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

        except Exception as error:
            print(
                "ERROR:",
                item["shop"],
                item["album"],
                error,
            )

            # 抓取失败时保持原状态
            # 不发库存变化通知
            continue

    save_state(
        new_state
    )

    if new_items:
        lines = [
            "✅ 新监控项目已建立",
            "",
        ]

        for item, status in new_items:
            lines.append(
                f"{item['shop']}｜"
                f"{item['album']}："
                f"{status.get('stock', '未知')}"
            )

        lines.extend(
            [
                "",
                "之后只有有效状态变化才会提醒。",
                "网页识别失败不会再误报为库存变化。",
                f"更新时间：{now_text()}",
            ]
        )

        telegram_send(
            "\n".join(lines)
        )


if __name__ == "__main__":
    main()
