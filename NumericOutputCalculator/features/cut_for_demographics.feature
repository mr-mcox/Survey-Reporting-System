Feature: When provided a set of demographics, cut by those demograhpics when specified

	Scenario: When provided a set of demographics, cut by one dimension
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
		Given demographic data
			| respondent_id | region  |
			| 1             | Atlanta |
			| 2             | Atlanta |
			| 3             | SoDak   |
		When compute net with cut_demographic = region is run
		Then the display_value including region for question_code 1 and region "Atlanta" is 0.5

	Scenario: When provided a set of demographics, cut by multiple dimensions
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
		When compute net with cut_demographic = region and gender is run
		Then the display_value including region and gender for question_code 1 and region "Atlanta" gender "Female" is 0.5

	Scenario: NumericOutputCalculator should only provide cut columns and display value
		Given net formatted values
				| respondent_id | question_code | net_formatted_value |
				| 1             | 1             | 1                   |
				| 2             | 1             | 0                   |
				| 3             | 1             | -1                  |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
		When compute net with cut_demographic = region is run
		Then the only columns returned are question_code, region, aggregation_value, result_type


	Scenario: When 7pt with 1=Strongly Agree questions are given, average is accurately computed
	Given raw 7pt questions responses
		| respondent_id | question_code | response |
		| 1             | 1             | 1        |
		| 2             | 1             | 1        |
		| 3             | 1             | 3        |
	Given demographic data
		| respondent_id | region  | gender |
		| 1             | Atlanta | Female |
		| 2             | Atlanta | Female |
		| 3             | SoDak   | Male   |
	When compute average with cut_demographic = region is run
	Then the display_value including region for question_code 1 and region "Atlanta" is 1
