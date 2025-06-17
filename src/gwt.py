import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import date, timedelta
import os
import json
from collections import defaultdict
from ai_analyse import *


base_url = 'https://nbw.sztu.edu.cn/'
gwt_data_path = os.path.join(os.path.dirname(__file__), 'data/gwt_data.csv')
response_data_path = os.path.join(os.path.dirname(__file__), 'data/response.txt')

def get_data_from_gwt(pages = 10, days_back = 2):
    # 栏目参数
    wbtreeid = '1029'
    total_pages = pages 
    date_today = date.today()
    date_from = date_today - timedelta(days=days_back)


    # CSV 存储
    with open(gwt_data_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['标题', '链接', '发布日期'])

        # 翻页循环
        for page_num in range(1, total_pages + 1):
            list_url = f'https://nbw.sztu.edu.cn/list.jsp?totalpage=603&PAGENUM={page_num}&urltype=tree.TreeTempUrl&wbtreeid={wbtreeid}'
            print(f'正在抓取第 {page_num} 页: {list_url}')

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
            response = requests.get(list_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取每个li
            for li in soup.select('li.clearfix'):
                title_tag = li.select_one('div.width04 a')
                if not title_tag:
                    continue  

                title = title_tag.get('title', '').strip()
                link = title_tag.get('href', '').strip()
                full_link = base_url + link if not link.startswith('http') else link

                # 提取日期
                date_div = li.select_one('div.width06')
                date_text = date_div.text.strip() if date_div else ''
                date_obj = date.fromisoformat(date_text)
                reach_date_range = False
                if date_obj < date_from:
                    reach_date_range = True
                    break

                writer.writerow([title, full_link, date_text])
            if reach_date_range:
                break

            time.sleep(1) 
    
def get_data_stored(delta = 2):
    date_today = date.today()


    date_from = date_today - timedelta(delta)

    result = []
    with open(gwt_data_path, 'r', newline='', encoding='utf-8-sig') as f:
       data = csv.DictReader(f)
       for post in data:
            date_post = date.fromisoformat(post['发布日期'])
            if date_post >= date_from and date_post <= date_today:
                result.append(post)
                continue
            if date_post < date_from:
                break
    
    return result
            
def analyze(data):
    with open('prompt.txt', 'r') as f:
        prompt = f.read()
    response = ai_response(prompt, data)
    return response

def output():
    file_path = os.path.join(os.path.dirname(__file__), 'response.txt')
    
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f: 
            json_str = f.read().strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            data = json.loads(json_str)
        
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
        return

    category_map = {
        1: "教学与学生管理",
        2: "科研与项目申报",
        3: "会议与培训活动",
        4: "党建与行政事务",
        5: "通知公告与后勤保障",
        6: "国际与校外交流合作"
    }

    audience_map = {
        1: "本科生",
        2: "研究生",
        3: "留学生",
        4: "全体学生",
        5: "教师",
        6: "全体师生"
    }

    if "message" in data and "summary" in data:
        print(data["message"])
        print(data["summary"])
        print()
    else:
        print("Error: JSON data does not contain 'message' or 'summary' keys.")
        return

    # 分组展示
    if "notices" in data and isinstance(data["notices"], list):
        grouped = defaultdict(list)
        for notice in data["notices"]:
            category_name = category_map.get(notice.get("category"), "未知分类")
            grouped[category_name].append(notice)

        for category, notices_list in grouped.items():
            print(f"\n📌 {category}：")
            for n in notices_list:
                audience = audience_map.get(n.get("audience"), "未知对象")
                print(f"- [{n.get('date', '未知日期')}] {n.get('title', '无标题')}（对象：{audience}）")
                print(f"  🔗 {n.get('link', '无链接')}")
    else:
        print("Error: JSON data does not contain a 'notices' list or it's not a list.")
        # print(f"Notices data: {data.get('notices')}")
