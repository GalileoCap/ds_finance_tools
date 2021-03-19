#INFO: Easy access to Google Sheets

from util.cfg import CFG
from util.misc import *
from util.pandas import *

from google.oauth2 import service_account
from googleapiclient.discovery import build

#U: Returns a range in A1	notation from two tuples
def range_A1(f, t):
	return to_A1(*f)+':'+to_A1(*t)

#U: Converts from numbers to A1 notation
def to_A1(row, col):
	col = LETTERS_AZ[(col - 1) % 26] * ((col - 1) // 26 + 1)
	row = str(row)
	return col+row

#U: Loads/Creates the credentials for api usage, and returns the client to make calls
Sheet = None
def init_sheets():
	#SEE: https://github.com/googleapis/google-api-python-client/blob/master/docs/oauth-server.md 
	global Sheet

	credentials = service_account.Credentials.from_service_account_file(
									CFG.service_account_file, scopes = CFG.google_scopes)

	Service = build('sheets', 'v4', credentials = credentials)
	Sheet = Service.spreadsheets()

#U: Gets the values from a range in the specified sheet, if range is None then it returns every cell
def get_from_sheet(id, sheet, _range = None):
	_Range = sheet
	if not _range is None:
		_Range += '!'+range_A1(*_range)

	result = Sheet.values().get(spreadsheetId = id, range = _Range).execute()
	values = result.get('values', [])

	return values

#U: Writes the cells in range with data
def set_to_sheet(id, sheet, data, _range = None):
	if _range is None: #A: Default range from the top-left corner
		_range = ((1, 1), (len(data), len(data[0])))
	_Range = sheet+'!'+range_A1(*_range)

	result = Sheet.values().update(spreadsheetId = id, range = _Range, valueInputOption = 'USER_ENTERED', body = {'values':data}).execute()

#U: Returns a df from a sheet's cells in range, using idx_col as the index
def get_df_from_sheet(id, sheet, _range = None, idx_col = 0):
	data = get_from_sheet(id, sheet, _range)
	return df_from_lol(data, idx_col)

#U: Writes the df into the given range
def set_df_to_sheet(id, sheet, df, _range = None):
	data = df_to_lol(df)
	set_to_sheet(id, sheet, data, _range)
