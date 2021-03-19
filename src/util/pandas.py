#INFO: Convert to and from DataFrames, etc.

import pandas as pd

def df_from_lol(data_lol, idx_col = 0): #U: Converts a list of lists into a DataFrame
	df = pd.DataFrame(data_lol[1:], columns = data_lol[0])

	if idx_col is None:
		pass
	else:
		if type(idx_col) == int:
			idx_col = data_lol[0][idx_col]
		df.set_index(idx_col, inplace = True)

	return df

def df_to_lol(df): #U: Converts a DataFrame into a list of lists
	tmp = df.reset_index()
	result = [tmp.columns.values.tolist()] + tmp.values.tolist()
	return result



