import sys
import os
from pathlib import Path
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from gwt import *
from main import *
from ai_analyse import *



# day = date(2025, 6, 15)
# # get_data_from_gwt()
# data = get_data_stored(day)

# result = ai_response(prompt, data)
# output(result.text)

# print(gwt_details_summary('https://nbw.sztu.edu.cn/info/1022/48984.htm'))
# print(gwt_classify())
talk_with_mashiro()