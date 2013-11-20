from bitstring import BitArray

class ConfigurationReader(object):
	"""docstring for ConfigurationReader"""
	def __init__(self, **kwargs):
		self.config = dict()
		self._all_dimensions = dict()

	def cuts_to_be_created(self):
		all_cut_fields = [{}]
		config = self.config
		assert 'cuts' in self.config
		assert type(config['cuts']) == dict

		for cut_title, cut in config['cuts'].items():
			assert 'dimensions' in cut
			assert type(cut['dimensions']) == list
			number_of_levels = len(cut['dimensions'])
			for i in range(2**number_of_levels):
				levels_for_this = []
				bit_mask = BitArray(uint=i,length=number_of_levels)
				for j, bit in enumerate(bit_mask):
					if bit == True:
						levels_for_this.append(cut['dimensions'][j])
				all_cut_fields.append(set(levels_for_this))
		return all_cut_fields

	def create_dimension(self, title):
		if title not in self._all_dimensions:
			new_dimension = Dimension()
			self._all_dimensions[title] = new_dimension
			return new_dimension
		else:
			return self._all_dimensions[title]

	def cuts():
		doc = "The cuts property."
		def fget(self):
			if not hasattr(self,'_cuts'):
				cuts = dict()
				config = self.config
				assert 'cuts' in config
				assert type(config['cuts']) == dict
				for cut_title, cut in config['cuts'].items():
					cuts[cut_title] = Cut(title=cut_title)
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
		self.title = kwargs.pop('title',None)
		config_object = kwargs.pop('config_object', None)
		if config_data != None:
			if 'dimensions' in config_data:
				assert type(config_data['dimensions']) == list
				if config_object != None:
					assert type(config_object) == ConfigurationReader
					self.dimensions = [config_object.create_dimension(x) for x in config_data['dimensions']]
				else:
					self.dimensions = [Dimension() for x in config_data['dimensions']]

class Dimension(object):
	def __init__(self,**kwargs):
		pass