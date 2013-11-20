import unittest
from CalculationCoordinator import CalculationCoordinator
import pandas as pd
import os, sys
from openpyxl import load_workbook
from openpyxl import Workbook
from unittest import mock
from SurveyReportingSystem.ConfigurationReader import ConfigurationReader

class WriteExcelTestCase(unittest.TestCase):

	def setUp(self):
		# assert not os.path.exists('test_file.xlsx')
		wb = Workbook()
		wb.save('test_file.xlsx')
		coordinator = CalculationCoordinator()
		self.mapping_values = ['dos','uno','tres']
		self.mapping_integers = ['2','1','3']
		self.mapping_dict = dict(zip(self.mapping_integers,self.mapping_values))
		self.labels_for_cut_dimensions = {
											'gender':{'male':'0','female':'1'},
											'region':{'Atlanta':'2','SoDak':'3'}
										}
		config_reader = ConfigurationReader.ConfigurationReader()
		config_reader.config =  {'cuts':{
								'Ethnicity': {'dimensions':['ethnicity']},
								'Region':{'dimensions':['region']}
								}}
		coordinator.config = config_reader
		coordinator.dimension_integer_mapping = {'values': self.mapping_values,'integers':self.mapping_integers}
		coordinator.excel_dashboard_file = 'test_file.xlsx'
		coordinator.labels_for_cut_dimensions = self.labels_for_cut_dimensions
		master_aggregation = pd.DataFrame({
				'row_heading':['0','0','1','1'],
				'column_heading': ['2.3','2.4','2.3','2.4'],
				'aggregation_value': [0.5,0.5,0.5,0.5]
			})
		with mock.patch.object(CalculationCoordinator, 'master_aggregation', new_callable=mock.PropertyMock) as m:
			m.return_value = master_aggregation
			coordinator.export_to_excel('test_file.xlsx')

	def test_writing_cut_config(self):
		ws = load_workbook(filename = r'test_file.xlsx').get_sheet_by_name(name = 'Lookups')

	def test_write_master_as_excel(self):
		ws = load_workbook(filename = r'test_file.xlsx').get_sheet_by_name(name = 'Sheet1')
		column_headings = [str(ws.cell(row=0,column=i+1).value) for i in range(ws.get_highest_column()-1)]
		self.assertEqual(set(column_headings), {'2.3','2.4'}) 
		row_headings = [str(ws.cell(row=i+1,column=0).value) for i in range(ws.get_highest_row()-1)]
		self.assertEqual(set(row_headings), {'0','1'})

	# def test_write_mappings(self):
	# 	ws = load_workbook(filename = r'test_file.xlsx').get_sheet_by_name(name = 'Lookups')
	# 	integer_column_values = [str(ws.cell(row=i,column=0).value) for i in range(ws.get_highest_row())]
	# 	value_column_values = [str(ws.cell(row=i,column=1).value) for i in range(ws.get_highest_row())]
	# 	integer_column_values_copy = [str(ws.cell(row=i,column=2).value) for i in range(ws.get_highest_row())]
	# 	self.assertEqual(value_column_values, self.mapping_values)
	# 	self.assertEqual(integer_column_values,self.mapping_integers)
	# 	self.assertEqual(integer_column_values_copy,self.mapping_integers)

	# def test_menus_with_values(self):
	# 	ws = load_workbook(filename = r'test_file.xlsx').get_sheet_by_name(name = 'Lookups')
	# 	gender_values = [str(ws.cell(row=i,column=3).value) for i in range(ws.get_highest_row())]
	# 	region_values = [str(ws.cell(row=i,column=4).value) for i in range(ws.get_highest_row())]
	# 	self.assertEqual(set(gender_values + region_values),{'gender','0','1','region','2','3'})

	def tearDown(self):
		try:
			pass
			os.remove('test_file.xlsx')
		except:
			pass


if __name__ == '__main__':
    unittest.main()