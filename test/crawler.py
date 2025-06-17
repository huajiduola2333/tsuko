import sys
import os
from datetime import date
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from gwt import *

day = date(2025, 6, 15)
get_data_from_gwt()
# print(get_data_stored(day))