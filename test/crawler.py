import sys
import os
from pathlib import Path
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from gwt import *
from ai_analyse import *

with open(os.path.join(os.path.dirname(__file__), '../res/prompt.txt'), 'r', encoding='utf-8') as f:
    prompt = f.read()

day = date(2025, 6, 15)
# get_data_from_gwt()
data = get_data_stored(day)

result = ai_response(prompt, data)
output(result.text)