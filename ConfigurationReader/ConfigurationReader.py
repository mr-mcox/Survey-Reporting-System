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
			assert 'cut_fields' in cut
			assert type(cut['cut_fields']) == list
			number_of_levels = len(cut['cut_fields'])
			for i in range(2**number_of_levels):
				levels_for_this = []
				bit_mask = BitArray(uint=i,length=number_of_levels)
				for j, bit in enumerate(bit_mask):
					if bit == True:
						levels_for_this.append(cut['cut_fields'][j])
				all_cut_fields.append(set(levels_for_this))
		return all_cut_fields