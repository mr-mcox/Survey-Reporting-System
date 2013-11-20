from bitstring import BitArray

class ConfigurationReader(object):
	"""docstring for ConfigurationReader"""
	def __init__(self, **kwargs):
		self.config = dict()

	def cuts_to_be_created(self):
		all_cut_fields = [{}]
		config = self.config
		assert 'cuts' in self.config
		assert type(config['cuts']) == list

		for cut in config['cuts']:
			assert 'levels' in cut
			assert type(cut['levels']) == list
			number_of_levels = len(cut['levels'])
			for i in range(2**number_of_levels):
				levels_for_this = []
				bit_mask = BitArray(uint=i,length=number_of_levels)
				for j, bit in enumerate(bit_mask):
					if bit == True:
						levels_for_this.append(cut['levels'][j])
				all_cut_fields.append(set(levels_for_this))
		return all_cut_fields

	def cuts():
		doc = "The cuts property."
		def fget(self):
			if not hasattr(self,'_cuts'):
				cuts = list()
				config = self.config
				assert 'cuts' in config
				assert type(config['cuts']) == list
				for cut in config['cuts']:
					cuts.append(Cut())
				self._cuts = cuts
			return self._cuts
		def fset(self, value):
			self._cuts = value
		def fdel(self):
			del self._cuts
		return locals()
	cuts = property(**cuts())

class Cut(object):
	def __init__(self, **kwargs):
		config_data = kwargs.pop('config_data',None)
		if config_data != None:
			if 'levels' in config_data:
				assert type(config_data['levels']) == list
				self.levels = [Level() for x in config_data['levels']]

class Level(object):
	def __init__(self, **kwargs):
		config_data = kwargs.pop('config_data',None)
		if config_data != None:
			assert type(config_data) == list
			self.dimensions = [Dimension() for x in config_data]

class Dimension(object):
	def __init__(self):
		pass