import pandas as pd

class NumericOutputCalculator(object):

	def __init__(self, *kwargs):
		
		net_results = kwargs.pop('net_formatted_values', None)

		return pd.DataFrame({'question_id':[1],'value':0})