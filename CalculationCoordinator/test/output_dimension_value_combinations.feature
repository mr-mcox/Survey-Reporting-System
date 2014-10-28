Feature: When assembling dimensions, show all value combinations so that there are values for excel to access (even if they are blank)
	Scenario: When a combination of values would not be shown for a cut because no values exist, add that combination in as to not screw up excel
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
		Given demographic data passed to coordinator
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Male   |
			| 3             | SoDak   | Male   |
		When ensure_combination_for_every_set_of_demographics is True
		Then compute net with cut_demographic = region and gender is run responses in row with SoDak and Female

	Scenario: When a combination of values would not be shown for a cut because no values exist, and the dimension type is 'dynamic', don't include that cut
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
		Given demographic data passed to coordinator
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Male   |
			| 3             | SoDak   | Male   |
		Given the gender ethnicity is "dynamic" with "dynamic_parent_dimension" of "region"
		When ensure_combination_for_every_set_of_demographics is True
		Then compute net with cut_demographic = region and gender is run responses in no rows with SoDak and Female


	Scenario: When there is a row in the demographics file but no row in the responses and the dimension is dynamic, don't include the row
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
		Given demographic data passed to coordinator
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Male   |
			| 3             | SoDak   | Female |
		Given the gender ethnicity is "dynamic" with "dynamic_parent_dimension" of "region"
		When ensure_combination_for_every_set_of_demographics is True
		Then compute net with cut_demographic = region and gender is run responses in no rows with SoDak and Female

	Scenario: When a combination of values would not be shown for a cut because no values exist, and the dimension type is 'dynamic' but parent dimension isn't in the cut, there should be a row 
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
		Given demographic data passed to coordinator
			| respondent_id | region  | gender | corps |
			| 1             | Atlanta | Female | 2012 |
			| 2             | Atlanta | Male   | 2013 |
			| 3             | SoDak   | Male   | 2013 |
		Given the gender ethnicity is "dynamic" with "dynamic_parent_dimension" of "region"
		When ensure_combination_for_every_set_of_demographics is True
		Then compute net with cut_demographic = region and gender is run responses in a row with 2013 and Female
