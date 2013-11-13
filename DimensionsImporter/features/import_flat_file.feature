Feature: Import of flat file
	
	Scenario: When an xlsx file is specified, a table of data is imported
		Given file cm_demographic_data.xlsx
		When DimensionsImporter is initialized with xlsx file
		Then demographic_data has a table with 6 rows