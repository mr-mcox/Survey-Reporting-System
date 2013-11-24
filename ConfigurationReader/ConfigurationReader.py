from bitstring import BitArray

class ConfigurationReader(object):
	"""docstring for ConfigurationReader"""
	def __init__(self, **kwargs):
		self.config = dict()
		self._all_dimensions = dict()
		self.number_of_levels = 3

	def cuts_to_be_created(self):
		all_cut_fields = [{}]
		config = self.config
		assert 'cuts' in self.config
		assert type(config['cuts']) == dict

		for cut_title, cut in self.cuts.items():
			assert type(cut.dimensions) == list
			number_of_levels = len(cut.dimensions)
			for i in range(2**number_of_levels):
				levels_for_this = []
				bit_mask = BitArray(uint=i,length=number_of_levels)
				for j, bit in enumerate(bit_mask):
					if bit == True:
						levels_for_this.append(cut.dimensions[j].title)
				all_cut_fields.append(set(levels_for_this))
		return all_cut_fields

	def cuts_for_excel_menu(self):
		cut_list = list()
		for cut_name, cut in self.cuts.items():
			assert type(cut) == Cut
			dimension_titles = [dimension.title for dimension in cut.dimensions]
			cut_list.append([cut.title, 'static'] + dimension_titles)
		return cut_list

	def create_dimension(self, title):
		if title not in self._all_dimensions:
			new_dimension = Dimension(title=title)
			self._all_dimensions[title] = new_dimension
			return new_dimension
		else:
			return self._all_dimensions[title]

	def all_dimensions(self):
		"""Returns a list of all dimnsions used by this ConfigurationReader"""
		return [dimension for key, dimension in self._all_dimensions.items()]

	def columns_for_row_header(self):
		return {cut.title:cut.dimensions for cut_title, cut in self.cuts.items()}
		
	def cuts():
		doc = "The cuts property."
		def fget(self):
			if not hasattr(self,'_cuts'):
				cuts = dict()
				config = self.config
				assert 'cuts' in config
				assert type(config['cuts']) == dict
				for cut_title, cut in config['cuts'].items():
					cuts[cut_title] = Cut(title=cut_title,config_object=self, config_data = cut)
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
		self.dimensions = list()
		config_object = kwargs.pop('config_object', None)
		if config_data != None:
			if 'dimensions' in config_data:
				assert type(config_data['dimensions']) == list
				if config_object != None:
					assert type(config_object) == ConfigurationReader
					self.dimensions = [config_object.create_dimension(x) for x in config_data['dimensions']]
				else:
					self.dimensions = [Dimension(title=x) for x in config_data['dimensions']]

class Dimension(object):
	def __init__(self,**kwargs):
		self.title = kwargs.pop('title',None)
		self.not_included_label = str(self.title) + " Not Used"