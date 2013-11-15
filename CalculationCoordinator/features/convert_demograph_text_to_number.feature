Feature: In order to allow any text to be used in cutting yet maintain sane sorting in excel, all demographics text should be converted to numbers

	Scenario: When multiple cuts are run, they are stored by tuple
		Given net formatted values
			| respondent_id | question_id | net_formatted_value |
			| 1             | 1           | 1     |
			| 2             | 1           | 0     |
			| 3             | 1           | -1    |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male |
		When compute net with cut_demographic = region and gender is run
		When compute net with cut_demographic = region is run
		Then computations_generated has a length of 2
		Then the display_value including region for question_id 1 and region "Atlanta" is 0.5

	Scenario: Identify all demographic columns across multiple cuts
		Given 