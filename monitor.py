import os
import re
import json
import html
import ssl
import smtplib
import urllib.request
import urllib.parse

from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.message import EmailMessage


BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

QQ_EMAIL = os.environ["QQ_EMAIL"]
QQ_SMTP_AUTH_CODE = os.environ["QQ_SMTP_AUTH_CODE"]
EMAIL_TO = [
    x.strip()
    for x in os.environ["EMAIL_TO"].split(",")
    if x.strip()
]

STATE_FILE = Path("state.json")


WATCHES = [
    # 佳佳
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

    # 环球 Fangoods
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

    # 五大
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

    # 滚石
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

    # 诚品
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

    # 九五
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
        "needles": ["阿密特2", "阿密特 2", "AMIT2", "AMIT 2"],
    },

    # 山海山
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

    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()

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
    price = first(r"網路價\s*NT\$\s*[:：]?\s*([\d,]+)", text)

    if "無庫存" in text:
        stock, available, valid = "无库存", False, True
    elif "加入購物車" in text or "現貨" in text:
        stock, available, valid = "可购买", True, True
    else:
        stock, available, valid = "状态暂未识别", False, False

    return {
        "stock": stock,
        "available": available,
        "price": f"NT${price}" if price else "",
        "note": "",
        "valid": valid,
    }


def parse_fangoods(text):
    stock_num = first(r"庫存量\s*[:：]?\s*(\d+)", text)
    price = first(r"價\s*格\s*[:：]?\s*\$?\s*([\d,]+)", text)

    if not stock_num:
        return {
            "stock": "库存数量未识别",
            "available": False,
            "price": "",
            "note": "",
            "valid": False,
        }

    n = int(stock_num)

    return {
        "stock": f"库存 {n}",
        "available": n > 0,
        "price": f"NT${price}" if price else "",
        "note": "",
        "valid": True,
    }


def parse_5music(text):
    if "目前無現貨" in text:
        stock, available, valid = "目前无现货", False, True
    elif (
        "加入購物車" in text
        or "放入購物車" in text
        or "ADD To cart" in text
        or "ADD TO CART" in text
    ):
        stock, available, valid = "可加入购物车", True, True
    else:
        stock, available, valid = "状态暂未识别", False, False

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": "",
        "valid": valid,
    }


def parse_rockmall(text):
    if "售完" in text:
        stock, available, valid = "售完", False, True
    elif "加入購物車" in text or "立即購買" in text:
        stock, available, valid = "可购买", True, True
    else:
        stock, available, valid = "状态暂未识别", False, False

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": "",
        "valid": valid,
    }


def parse_eslite(text):
    if (
        "貨到通知" in text
        or "預購完銷" in text
        or "再版預購完銷" in text
        or "缺貨" in text
        or "暫無庫存" in text
    ):
        stock, available, valid = "暂不可购买", False, True
    elif (
        "加入購物車" in text
        or "立即購買" in text
        or "再版預購中" in text
    ):
        stock, available, valid = "可购买/预购", True, True
    else:
        stock, available, valid = "状态暂未识别", False, False

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": "",
        "valid": valid,
    }


def parse_line(text, needles):
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    matched = ""

    for line in lines:
        if any(n.lower() in line.lower() for n in needles):
            matched = line
            break

    if not matched:
        return {
            "stock": "页面未找到",
            "available": False,
            "price": "",
            "note": "",
            "valid": False,
        }

    negatives = ["無庫存", "无库存", "售完", "完銷", "缺貨", "缺货"]
    positives = ["現貨", "现货", "有庫存", "有库存", "加入購物車", "可購買"]

    if any(x in matched for x in negatives):
        stock, available = "暂不可购买", False
    elif any(x in matched for x in positives):
        stock, available = "可能可购买", True
    else:
        stock, available = "已上架，库存待确认", False

    return {
        "stock": stock,
        "available": available,
        "price": "",
        "note": matched[:220],
        "valid": True,
    }


def check_item(item):
    text = visible_text(fetch(item["url"]))

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
        result = parse_line(text, item["needles"])
    else:
        raise ValueError("Unknown parser type")

    result["checked_at"] = now_text()
    return result


def telegram_send(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": "true",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")

    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()


def email_send(subject, body):
    msg = EmailMessage()
    msg["From"] = QQ_EMAIL
    msg["To"] = ", ".join(EMAIL_TO)
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        "smtp.qq.com",
        465,
        context=context,
        timeout=30,
    ) as smtp:
        smtp.login(QQ_EMAIL, QQ_SMTP_AUTH_CODE)
        smtp.send_message(msg)


def notify_all(subject, body):
    telegram_send(body)
    email_send(subject, body)


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
        "stock": status.get("stock", ""),
        "available": status.get("available", False),
        "price": status.get("price", ""),
        "note": status.get("note", ""),
    }


def format_message(item, old, new):
    if new.get("available") and not old.get("available"):
        title = "🚨 张惠妹专辑到货 / 恢复购买"
    else:
        title = "🔔 张惠妹专辑状态变化"

    lines = [
        title,
        "",
        f"专辑：{item['album']}",
        f"平台：{item['shop']}",
        f"原状态：{old.get('stock', '未知')}",
        f"最新状态：{new.get('stock', '未知')}",
    ]

    if new.get("price"):
        lines.append(f"价格：{new['price']}")

    if new.get("note"):
        lines.append(f"页面信息：{new['note']}")

    lines += [
        f"发现时间：{new['checked_at']}",
        item["url"],
    ]

    return "\n".join(lines)


def main():
    old_state = load_state()
    new_state = dict(old_state)

    # 第一次启用邮箱时只测试一次
    if not old_state.get("__email_test_sent__"):
        test_body = (
            "✅ A-MEI Album Monitor 邮件通知已启用\n\n"
            "以后《偏执面》《偷故事的人》《AMIT 2》出现有效库存变化时，"
            "会同时通过 Telegram、QQ邮箱和 Gmail 通知你。\n\n"
            f"测试时间：{now_text()}"
        )

        email_send(
            "A-MEI Album Monitor 邮件通知测试",
            test_body,
        )

        telegram_send(
            "✅ 邮件通知已启用\n"
            "QQ邮箱 + Gmail 测试邮件已发送。"
        )

        new_state["__email_test_sent__"] = True

    for item in WATCHES:
        try:
            status = check_item(item)

            if not status.get("valid", False):
                print("SKIP:", item["shop"], item["album"])
                continue

            old = old_state.get(item["id"])
            new_state[item["id"]] = status

            if old is None:
                continue

            if comparable(old) != comparable(status):
                body = format_message(item, old, status)

                notify_all(
                    f"A-MEI 到货提醒｜{item['album']}｜{item['shop']}",
                    body,
                )

        except Exception as e:
            print("ERROR:", item["shop"], item["album"], e)

    save_state(new_state)


if __name__ == "__main__":
    main()
