Feature: When assembling dimensions, show all value combinations so that there are values for excel to access (even if they are blank)

	Scenario: When a combination of values would not be shown for a cut because no values exist, add that combination in as to not screw up excel
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Male   |
			| 3             | SoDak   | Male   |
		Given ensure_combination_for_every_set_of_demographics is True
		When compute net with cut_demographic = region and gender is run
		Then there is a row with SoDak and Female