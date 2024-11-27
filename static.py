# -*- coding: utf-8 -*-

import ssl
import requests
import time
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
import sys
import importlib

importlib.reload(sys)  # Reload the sys module (though it's rarely needed in Python 3)

ssl._create_default_https_context = ssl._create_unverified_context
old_time_stamp = "2023/03/26;09:59:49"
new_time_stamp = "0"
new_time_stamp2 = "0"
repeat_flag = 0  # Initialize repeat_flag
repeat_flag2 = 0

def Stockparser(url):
    global old_time_stamp
    global new_time_stamp
    global repeat_flag  # Declare repeat_flag as global
    global new_time_stamp2
    global repeat_flag2
    global msg
    global msg2

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
    except:
        print("url fail")
        sleep(300)
        return '', 1, 1
    try:
        # Locate the specified table
        table = soup.find("table", attrs={"class": "gvTB gvTB_TWSE"})
        rows = table.find_all("tr")
        cols = rows[1].find_all("td")
        msg = ("三大法人買賣超:\n"
               "日期:" + cols[0].text.strip() +
               " 外資" + cols[1].text.strip() +
               " 投信" + cols[2].text.strip() +
               " 自營" + cols[3].text.strip() +
               "\n總計:" + cols[6].text.strip())

    except:
        print("No table!!")
        return '', 1, 1

    # Check for timestamp changes
    if repeat_flag == 0:
        new_time_stamp = datetime.now().strftime("%m/%d")
    if new_time_stamp != cols[0].text.strip():
        new_time_stamp = cols[0].text.strip()
        repeat_flag = 0

    try:
        # Locate the second specified table
        table_item = soup.find_all('div', class_='grid-item ml10')
        rows = table_item[0].find("table", attrs={"class": "gvTB"})
        row = rows.find_all("tr")
        cols = row[1].find_all("td")
        msg2 = ("台股期貨未平倉:\n"
                "日期:" + cols[0].text.strip() +
                " 外資" + cols[1].text.strip() +
                " 投信" + cols[2].text.strip() +
                " 自營" + cols[3].text.strip() +
                "\n總計:" + cols[4].text.strip())

        if repeat_flag2 == 0:
            new_time_stamp2 = datetime.now().strftime("%m/%d")
        if new_time_stamp2 != cols[0].text.strip() and cols[1].text.strip() != "0":
            print(cols[0].text.strip())
            new_time_stamp2 = cols[0].text.strip()
            repeat_flag2 = 0

    except:
        return '', 1, 1

    return msg, repeat_flag, repeat_flag2

def LineNotify(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    params = {
        "message": msg
    }
    r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=params)

def DiscordNotify(webhook_url, msg):
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "content": msg
    }
    response = requests.post(webhook_url, json=payload, headers=headers)
    if response.status_code != 204:
        print("Failed to send message.")

if __name__ == "__main__":
    webhook_url = "https://discordapp.com/api/webhooks/1308682093462683709/jUSEVpXsVDoKiF-aFnQKTmcx2gXDUKuN213R8QAy5xTJxMvVNoquRpUwYYDHoOae41ye"
    token = "82JoR58J42E8z3VTQ60U3RMWk5DysWiHe60WN8uWbRX"  # LINE Notify token
    url = "https://histock.tw/stock/three.aspx"  # Target URL

    while True:
        now = datetime.now()
        current_time = now.strftime("%Y/%m%d %H:%M:%S")
        print(current_time.strip())
        msg, repeat_flag, repeat_flag2 = Stockparser(url)
        
        # Send messages once and set corresponding flags
        if repeat_flag == 0:
            print(msg)
            LineNotify(token, msg + url)
            DiscordNotify(webhook_url, msg)
            repeat_flag = 1

        if repeat_flag2 == 0:
            print(msg2)
            LineNotify(token, msg2 + url)
            DiscordNotify(webhook_url, msg2)
            repeat_flag2 = 1

        time.sleep(300)  # Check every 5 minutes

