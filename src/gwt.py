import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import date, timedelta
from pathlib import Path
import json
from collections import defaultdict
from ai_analyse import *
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / 'data'

base_url = 'https://nbw.sztu.edu.cn/'
gwt_data_path = DATA_DIR / 'gwt_data.csv'
response_data_path = DATA_DIR / 'response.txt'

def get_data_from_gwt(max_pages = 1):
    wbtreeid = '1029'
    total_pages = max_pages
    date_today = date.today()
    # date_from_config = date_today - timedelta(days=days_back)

    last_link = None
    last_date_obj = None
    existing_df = pd.DataFrame(columns=['标题', '链接', '发布日期'])

    if gwt_data_path.exists() and gwt_data_path.stat().st_size > 0:
        try:
            current_data_df = pd.read_csv(gwt_data_path, dtype={'链接': str, '发布日期': str})
            if not current_data_df.empty:
                existing_df = current_data_df
                last_link = existing_df.iloc[0]['链接']
                try:
                    last_date_obj = date.fromisoformat(existing_df.iloc[0]['发布日期'])
                except ValueError:
                    print(f"Warning: Could not parse date from existing CSV's first row: {existing_df.iloc[0]['发布日期']}")
                    last_date_obj = None
        except pd.errors.EmptyDataError:
            print(f"Info: {gwt_data_path} is empty or contains only headers.")
        except Exception as e:
            print(f"Error reading existing CSV {gwt_data_path}: {e}")

    new_rows_list = []
    stop_scraping = False

    for page_num in range(1, total_pages + 1):
        if stop_scraping:
            break
        list_url = f'https://nbw.sztu.edu.cn/list.jsp?totalpage=603&PAGENUM={page_num}&urltype=tree.TreeTempUrl&wbtreeid={wbtreeid}'
        print(f'正在抓取第 {page_num} 页: {list_url}')

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        try:
            response = requests.get(list_url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page_num}: {e}")
            continue # Skip to next page

        soup = BeautifulSoup(response.text, 'html.parser')

        for li in soup.select('li.clearfix'):
            title_tag = li.select_one('div.width04 a')
            if not title_tag:
                continue

            title = title_tag.get('title', '').strip()
            link_path = title_tag.get('href', '').strip()
            full_link = base_url + link_path if not link_path.startswith('http') else link_path

            date_div = li.select_one('div.width06')
            date_text = date_div.text.strip() if date_div else ''
            
            try:
                current_item_date_obj = date.fromisoformat(date_text)
            except ValueError:
                print(f"Warning: Could not parse date '{date_text}' for item '{title}'. Skipping.")
                continue

            if full_link == last_link:
                print(f"达到上次爬到的记录开头: {full_link}")
                stop_scraping = True
                break
            
            if last_date_obj and current_item_date_obj < last_date_obj:
                print(f"当前记录日期 {current_item_date_obj} 早于上次最新记录日期 {last_date_obj}。")
                stop_scraping = True
                break

            # if current_item_date_obj < date_from_config:
            #     print(f"当前记录日期 {current_item_date_obj} 早于设定的截止日期 {date_from_config} ({days_back} 天前)。")
            #     stop_scraping = True
            #     break
            
            new_rows_list.append({'标题': title, '链接': full_link, '发布日期': date_text})
        
        if stop_scraping:
            break
        time.sleep(1)
    
    if not new_rows_list:
        print("没有爬取到新数据。")
        # Ensure file exists with headers if it was initially empty and no new data
        if existing_df.empty: # Covers file not existing or being empty initially
             final_df_to_save = pd.DataFrame(columns=['标题', '链接', '发布日期'])
        else: # existing_df has data, but no new data, so save existing_df (e.g. to ensure sort/unique)
             final_df_to_save = existing_df
    else:
        new_df = pd.DataFrame(new_rows_list)
        # New data is scraped newest first. Concatenate new data before existing.
        combined_df = pd.concat([new_df, existing_df], ignore_index=True)
        final_df_to_save = combined_df

    # Process the DataFrame to be saved (either combined or just existing/new)
    if not final_df_to_save.empty:
        # Remove duplicates, keeping the first occurrence (which is the newest from concat or scrape)
        final_df_to_save = final_df_to_save.drop_duplicates(subset=['链接'], keep='first')
        
        # Sort by '发布日期' descending (newest first)
        try:
            final_df_to_save['temp_date_col'] = pd.to_datetime(final_df_to_save['发布日期'])
            final_df_to_save = final_df_to_save.sort_values(by='temp_date_col', ascending=False).drop(columns=['temp_date_col'])
        except Exception as e:
            print(f"警告: 由于解析错误，无法按日期排序: {e}。数据未按日期排序保存。")
    elif final_df_to_save.columns.empty: # Ensure columns if df is completely empty
        final_df_to_save = pd.DataFrame(columns=['标题', '链接', '发布日期'])


    final_df_to_save.to_csv(gwt_data_path, index=False, encoding='utf-8-sig')
    
    if new_rows_list:
        print(f"保存了 {len(new_rows_list)} 条新记录。CSV中总记录数: {len(final_df_to_save)}.")
    elif not existing_df.equals(final_df_to_save):
         print(f"数据已重新处理 (例如排序/去重)。CSV中总记录数: {len(final_df_to_save)}.")
    else:
        print(f"CSV文件未发生变化。总记录数: {len(final_df_to_save)}.")

def get_data_stored(delta = 2, date_from = date.today()):
    date_from_filter = date_from - timedelta(days=delta)
    result = []

    if not gwt_data_path.exists() or gwt_data_path.stat().st_size == 0:
        print(f"Info: {gwt_data_path} 不存在或为空。")
        return result

    try:
        df = pd.read_csv(gwt_data_path, dtype={'链接': str, '发布日期': str})
        if df.empty:
            return result

        if '发布日期' in df.columns:
            # Convert '发布日期' to actual date objects for comparison
            # NaT for errors, then filter out NaT before comparison
            df['parsed_date'] = pd.to_datetime(df['发布日期'], errors='coerce').dt.date
            
            # Filter out rows where date parsing failed
            valid_dates_df = df.dropna(subset=['parsed_date'])
            
            mask = (valid_dates_df['parsed_date'] >= date_from_filter) & \
                   (valid_dates_df['parsed_date'] <= date_from)
            filtered_df = valid_dates_df[mask]
            
            result = filtered_df[['标题', '链接', '发布日期']].to_dict('records')
        else:
            print("警告: CSV文件中未找到 '发布日期' 列。无法按日期筛选。")

    except pd.errors.EmptyDataError:
        print(f"Info: {gwt_data_path} 为空。无法获取数据。")
    except Exception as e:
        print(f"在 get_data_stored 中读取或处理 {gwt_data_path} 时出错: {e}")
    
    return result
            
def analyze(data):
    with open('prompt.txt', 'r') as f:
        prompt = f.read()
    response = ai_response(prompt, data)
    return response

def output(response):
    file_path = response_data_path
    
    # try:
    #     with open(file_path, "r", encoding="utf-8-sig") as f: 
    #         json_str = f.read().strip()
    #         if json_str.startswith("```json"):
    #             json_str = json_str[7:]
    #         if json_str.endswith("```"):
    #             json_str = json_str[:-3]
    #         json_str = json_str.strip()
    #         data = json.loads(json_str)
        
    # except FileNotFoundError:
    #     print(f"Error: The file '{file_path}' was not found.")
    #     return
    # except json.JSONDecodeError as e:
    #     print(f"Error decoding JSON from '{file_path}': {e}")
    #     return
    
    json_str = response.strip()
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    json_str = json_str.strip()
    data = json.loads(json_str)

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
