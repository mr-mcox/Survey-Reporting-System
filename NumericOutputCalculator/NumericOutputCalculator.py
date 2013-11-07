import pandas as pd

class NumericOutputCalculator(object):

	def __init__(self, **kwargs):
		
		net_formatted_values = kwargs.pop('net_formatted_values', None)
		raw_values = kwargs.pop('raw_values', None)
		if net_formatted_values == None:
			map_7pt_SA_to_net = {8:None,7:1,6:1,5:0,4:-1,3:-1,2:-1,1:-1}
			net_formatted_values = pd.DataFrame(raw_values)
			net_formatted_values.value = net_formatted_values.value.map(map_7pt_SA_to_net)
		net_formatted_values = pd.DataFrame(net_formatted_values)
		self.net_formatted_values = net_formatted_values

	# def map_7pt_SA_to_net(value):
	# 	if(value == 6 or value == 7):
	# 		return 1
	# 	if(value < 5):
	# 		return -1
	# 	if(value==4):
	# 		return 0
	# 	else:
	# 		return None

	def compute_net_results(self):
		return self.net_formatted_values.groupby('question_id').mean().reset_index()

	def compute_strong_results(self):
		data = self.net_formatted_values.copy()
		data.ix[data.value.notnull() & (data.value != 1),'value'] = 0
		return data.groupby('question_id').mean().reset_index()
	
	def compute_weak_results(self):
		data = self.net_formatted_values.copy()
		data.ix[data.value.notnull() & (data.value != -1),'value'] = 0
		data.value = data.value * -1
		return data.groupby('question_id').mean().reset_index()
