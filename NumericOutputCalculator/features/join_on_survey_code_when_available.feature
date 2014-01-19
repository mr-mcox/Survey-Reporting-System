Feature: When demographics and results have survey code, join on both fields
		Scenario: When provided a set of demographics, cut by one dimension
		Given net formatted values
			| respondent_id | question_code | net_formatted_value | survey_code |
			| 1             | 1             | 1                   | 1314F8W |
			| 1             | 1             | -1                  | 1314MYS |
		Given demographic data
			| respondent_id | region  | survey_code |
			| 1             | Atlanta | 1314F8W |
			| 1             | Chicago | 1314MYS |
		When NumericOutputCalculator is initialized with results and demographic_data
		Then results_with_dimensions has region of "Atlanta" for respondent_id 1 and survey_code "1314F8W"
		Then results_with_dimensions has region of "Chicago" for respondent_id 1 and survey_code "1314MYS"