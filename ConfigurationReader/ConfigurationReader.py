class ConfigurationReader(object):
	"""docstring for ConfigurationReader"""
	def __init__(self, **kwargs):
		self.config = dict()

	def cuts_to_be_created(self):
		all_cut_fields = [[]]
		config = self.config
		assert 'cuts' in self.config
		assert type(config['cuts']) == list

		for cut in config['cuts']:
			assert 'cut_fields' in cut
			assert type(cut['cut_fields']) == list
			all_cut_fields.append(cut['cut_fields'])
		return all_cut_fields