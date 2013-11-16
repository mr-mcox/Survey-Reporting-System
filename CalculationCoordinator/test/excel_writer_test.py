import unittest
from CalculationCoordinator import CalculationCoordinator
import pandas as pd
import os
from openpyxl import load_workbook
from unittest import mock

class WriteExcelTestCase(unittest.TestCase):
	def test_write_master_as_excel(self):
		master_aggregation = pd.DataFrame({
				'row_heading':['0','0','1','1'],
				'column_heading': ['2.3','2.4','2.3','2.4'],
				'aggregation_value': [0.5,0.5,0.5,0.5]
			})

		with mock.patch.object(CalculationCoordinator, 'master_aggregation', new_callable=mock.PropertyMock) as m:
			m.return_value = master_aggregation
			coordinator = CalculationCoordinator()
			assert not os.path.exists('test_file.xlsx')
			coordinator.export_to_excel('test_file.xlsx')
		ws = load_workbook(filename = r'test_file.xlsx').get_sheet_by_name(name = 'Sheet1')
		column_headings = [str(ws.cell(row=0,column=i+1).value) for i in range(ws.get_highest_column()-1)]
		self.assertEqual(set(column_headings), {'2.3','2.4'}) 
		row_headings = [str(ws.cell(row=i+1,column=0).value) for i in range(ws.get_highest_row()-1)]
		self.assertEqual(set(row_headings), {'0','1'})

	def tearDown(self):
		try:
			pass
			os.remove('test_file.xlsx')
		except:
			pass

if __name__ == '__main__':
    unittest.main()