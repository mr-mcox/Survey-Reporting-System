import pandas as pd
from SurveyReportingSystem.NumericOutputCalculator import NumericOutputCalculator

class CalculationCoordinator(object):
	"""docstring for CalculationCoordinator"""
	def __init__(self, **kwargs):
		self.results = kwargs.pop('results',None)
		self.demographic_data = kwargs.pop('demographic_data',None)
		self.computations_generated = dict()	

	def get_aggregation(self,**kwargs):
		cuts = kwargs.pop('cuts',None)
		result_type = kwargs.pop('result_type',None)
		
		if type(cuts) != list:
			cuts = [cuts]
		aggregation_key = tuple(cuts + [result_type])

		assert aggregation_key in self.computations_generated
		return self.computations_generated[aggregation_key]

	def compute_aggregation(self,**kwargs):
		calculator = NumericOutputCalculator.NumericOutputCalculator(net_formatted_values=self.results,demographic_data=self.demographic_data)
		calculations = calculator.compute_aggregation(**kwargs)

		cuts = kwargs.pop('cut_demographic',None)
		result_type = kwargs.pop('result_type',None)

		if type(cuts) != list:
			cuts = [cuts]
		aggregation_key = tuple(cuts + [result_type])

		self.computations_generated[aggregation_key] = calculations