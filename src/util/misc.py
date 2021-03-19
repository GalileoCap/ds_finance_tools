#INFO: General purpose functions

import os
from datetime import datetime
import string

LETTERS_AZ = list(string.ascii_lowercase)

def get_file_mtime(fpath): #U: Date of last change or 0 
	try:
		stat = os.stat(fpath)
		return stat.st_mtime
	except:
		return 0

def isFromToday_file(fpath): #U: True if the file is from today
	today = datetime.today().day
	file_day = datetime.fromtimestamp(get_file_mtime(fpath)).day
	return file_day == today
