import pandas as pd

class DimensionsImporter(object):
	"""docstring for DimensionsImporter"""
	def __init__(self, **kwargs):
		input_file = kwargs.pop('flat_file', None)
		self.demographic_data = pd.read_excel(input_file,'Sheet1')