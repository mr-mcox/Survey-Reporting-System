Feature: Import of flat file
	
	Scenario: When an xlsx file is specified, a table of data is imported
		Given file cm_demographic_data.xlsx
		And DimensionsImporter is initialized with xlsx file
		Then demographic_data has a table with 6 rows

	Scenario: When demographic_data is assigned a table with a column names that should be interpreted as respondent_id, the column name is changed
		Given demographic input data
			| cm_pid | region |
			| 0 | Atlanta|
		And an importer
		When this data is assigned to demographic_data
		Then demographic_data has a column titled "respondent_id"

	Scenario: When an xlsx file with blank_rows is specified, only records with non-blank respondent_ids are loaded
		Given file cm_demographic_data_with_blank_rows.xlsx
		And DimensionsImporter is initialized with xlsx file
		Then demographic_data has a table with 6 rows