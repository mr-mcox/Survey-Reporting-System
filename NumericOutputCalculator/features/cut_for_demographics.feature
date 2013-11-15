Feature: When provided a set of demographics, cut by those demograhpics when specified

	Scenario: When provided a set of demographics, cut by one dimension
		Given net formatted values
			| respondent_id | question_id | value |
			| 1             | 1           | 1     |
			| 2             | 1           | 0     |
			| 3             | 1           | -1    |
		Given demographic data
			| respondent_id | region  |
			| 1             | Atlanta |
			| 2             | Atlanta |
			| 3             | SoDak   |
		When compute net with cut_demographic = region is run
		Then the display_value including region for question_id 1 and region "Atlanta" is 0.5

	Scenario: When provided a set of demographics, cut by multiple dimensions
		Given net formatted values
			| respondent_id | question_id | value |
			| 1             | 1           | 1     |
			| 2             | 1           | 0     |
			| 3             | 1           | -1    |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male |
		When compute net with cut_demographic = region and gender is run
		Then the display_value including region and gender for question_id 1 and region "Atlanta" gender "Female" is 0.5
