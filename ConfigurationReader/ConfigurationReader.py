from bitstring import BitArray
import yaml
import logging
import copy

class ConfigurationReader(object):
	"""docstring for ConfigurationReader"""
	def __init__(self, **kwargs):
		self.config = dict()
		self._all_dimensions = dict()
		self.default_number_of_levels = 3
		self.config_file = kwargs.pop('config_file',None)
		if self.config_file != None:
			stream = open(self.config_file,'r')
			self.config = yaml.load(stream)

	def cuts_to_be_created(self):
		all_cut_fields = []
		config = self.config
		assert 'cuts' in self.config
		assert type(config['cuts']) == dict

		for cut_title, cut in self.cuts.items():
			assert type(cut.dimensions) == list
			number_of_levels = len(cut.dimensions)
			zero_fill = [None for x in range(self.default_number_of_levels - number_of_levels )]
			for i in range(2**number_of_levels):
				levels_for_this_variation = []
				list_of_levels_for_this_variation = [levels_for_this_variation]
				bit_mask = BitArray(uint=i,length=number_of_levels)
				for j, bit in enumerate(bit_mask):
					if bit == True:
						if self.get_dimension_by_title(cut.dimensions[j].title).is_composite:
							base_levels = copy.deepcopy(list_of_levels_for_this_variation)
							list_of_levels_for_this_variation = []
							for dimension in self.get_dimension_by_title(cut.dimensions[j].title).composite_dimensions:
								base_levels_copy = copy.deepcopy(base_levels)
								for item in base_levels_copy:
									item.append(dimension)
								list_of_levels_for_this_variation = list_of_levels_for_this_variation + base_levels_copy
						else:
							for item in list_of_levels_for_this_variation:
								item.append(cut.dimensions[j].title)
					else:
						for item in list_of_levels_for_this_variation:
							item.append(None)
				for item in list_of_levels_for_this_variation:
					all_cut_fields.append(item + zero_fill)
		return all_cut_fields

	def cuts_for_excel_menu(self):
		cut_list = list()
		all_dimensions = {dimension.title: dimension for dimension in self.all_dimensions()}
		for cut_name, cut in self.cuts.items():
			assert type(cut) == Cut
			dimension_titles = [dimension.title for dimension in cut.dimensions]
			cut_list.append([cut.title, all_dimensions[dimension_titles[0]].dimension_type] + dimension_titles)
		return cut_list

	def create_dimension(self, title):
		if title not in self._all_dimensions:
			dimension_config = None
			if 'dimensions' in self.config and title in self.config['dimensions']:
				dimension_config = self.config['dimensions'][title]
			new_dimension = Dimension(title=title, config = dimension_config)
			self._all_dimensions[title] = new_dimension

			#Create dimension if it doesn't already exist
			if new_dimension.is_composite:
				for dimension in new_dimension.composite_dimensions:
					self.create_dimension(dimension)
			return new_dimension
		else:
			return self._all_dimensions[title]

	def all_dimensions(self):
		"""Returns a list of all dimnsions used by this ConfigurationReader"""
		return [dimension for key, dimension in self._all_dimensions.items()]

	def get_dimension_by_title(self,dimension):
		assert dimension in self._all_dimensions, "Dimension " + dimension + " is asked for but doesn't exit yet"
		return self._all_dimensions[dimension]

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
					cut_dimensions = list()
					for dimension_name in config_data['dimensions']:
						cut_dimensions.append(config_object.create_dimension(dimension_name))

					self.dimensions = cut_dimensions
				else:
					self.dimensions = [Dimension(title=x) for x in config_data['dimensions']]

class Dimension(object):
	def __init__(self,**kwargs):
		self.config = kwargs.pop('config',None)
		self.title = kwargs.pop('title',None)
		self.all_together_label = None
		self.dimension_type = "static"
		self.is_composite = False
		self.value_order = None
		if self.config is not None:
			if 'all_together_label' in self.config:
				self.all_together_label = self.config['all_together_label']
			if 'dynamic_parent_dimension' in self.config:
				self.dimension_type = "dynamic"
				self.dynamic_parent_dimension = self.config['dynamic_parent_dimension']
			if 'composite_dimensions' in self.config:
				self.is_composite = True
				self.composite_dimensions = self.config['composite_dimensions']
			if 'value_order' in self.config:
				assert type(self.config['value_order']) is list
				self.value_order = self.config['value_order']
				self.value_order