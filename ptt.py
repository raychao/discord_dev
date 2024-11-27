import requests
from bs4 import BeautifulSoup
import urllib.parse
from time import sleep
from datetime import datetime

# 儲存已經顯示過的文章的 URL
displayed_urls = set()

def get_articles_on_ptt(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        articles = []
    except:
        sleep(300)
        return '',''

    for i in soup.find_all('div', 'r-ent'):
        meta = i.find('div', 'title').find('a')
        title = meta.getText().strip() if meta else "標題未知"
        url = urllib.parse.urljoin(url, meta.get('href')) if meta else None
        articles.append({
            'title': title,
            'url': url,
            'push': i.find('div', 'nrec').getText(),
            'date': i.find('div', 'date').getText(),
            'author': i.find('div', 'author').getText(),
        })
    try:
        next_link = soup.find('div', 'btn-group-paging').find_all('a', 'btn')[1].get('href')
    except:
        return '',''
    return articles, next_link

def get_pages(board, num, search_conditions=None):
    if board == 'movie':
        index = "https://www.ptt.cc/bbs/movie/index.html"
    elif board == 'stock':
        index = "https://www.ptt.cc/bbs/stock/index.html"
    else:
        raise ValueError('Unsupported board:', board)
    
    page_url = index
    all_articles = []

    for j in range(num):
        articles, next_link = get_articles_on_ptt(page_url)
        if articles == '':
            return ''
        all_articles += articles
        page_url = urllib.parse.urljoin(index, next_link)
    
    if search_conditions:
        matching_articles = []
        for article in all_articles:
            is_match = True
            for condition_key, condition_value in search_conditions.items():
                if condition_value:
                    if condition_key == 'board':
                        continue
                    elif condition_key == 'title':
                        if condition_value not in article['title']:
                            is_match = False
                            break
                    elif condition_key == 'author':
                        if condition_value not in article['author']:
                            is_match = False
                            break
            if is_match and article['url'] not in displayed_urls:
                matching_articles.append(article)
                displayed_urls.add(article['url'])
        return matching_articles
    else:
        return all_articles

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
    now = datetime.now()
    current_time = now.strftime("%Y/%m%d %H:%M:%S")
    print(current_time)
    # 定義搜索條件列表
    search_conditions = [
        {'board': 'stock', 'title': '合一'},
        {'board': 'stock', 'title': '中工'},
        {'board': 'stock', 'title': '興富發'},
        {'board': 'stock', 'title': '中天'},
        {'board': 'stock', 'title': '鑽石'},
        {'board': 'stock', 'author': 'MrChen'},
        {'board': 'stock', 'author': 'robertshih'},
        {'board': 'stock', 'author': 'zesonpso'},
        {'board': 'stock', 'author': 'Test520'},
        {'board': 'stock', 'author': 'chanjay'}
    ]
    token = "82JoR58J42E8z3VTQ60U3RMWk5DysWiHe60WN8uWbRX"
    webhook_url = "https://discordapp.com/api/webhooks/1308682093462683709/jUSEVpXsVDoKiF-aFnQKTmcx2gXDUKuN213R8QAy5xTJxMvVNoquRpUwYYDHoOae41ye"
    while True:
        for condition in search_conditions:
            board = condition['board']
            matched_articles = get_pages(board, num=5, search_conditions=condition)
            if matched_articles:
                print('\n以下是在 {} 版中符合條件的新文章:'.format(board))
                for article in matched_articles:
                    print('標題:', article['title'])
                    print('作者:', article['author'])
                    print('日期:', article['date'])
                    
                    # 檢查 URL 是否為完整的
                    if article['url'].startswith("http"):
                        url = article['url']
                    else:
                        url = "https://www.ptt.cc" + article['url']
                    
                    print('URL:', url)
                    print('---')

                    # 發送 LINE 通知
                    msg = "{} - {}".format(article['title'], url)
                    LineNotify(token, msg)
                    DiscordNotify(webhook_url, msg)
        
        # 等待五分鐘再次執行搜索
        sleep(300)  # 300 秒 = 5 分鐘
        now = datetime.now()
        current_time = now.strftime("%Y/%m%d %H:%M:%S")
        print(current_time)
