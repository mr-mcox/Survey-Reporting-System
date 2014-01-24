Feature: Questions that have categorical and ordered question code are computed as the percent that fall into each of the responses

	Scenario: When net is run, the computations are accurately made
		Given raw 7pt questions results
			| question_code | response | question_type        |
			| 1             | 1        | Categorical_response |
			| 1             | 1        | Categorical_response |
			| 1             | 1        | Categorical_response |
			| 1             | 2        | Categorical_response |
			| 1             | 2        | Categorical_response |
			| 2             | 2        | 7pt_1=SA             |
		When compute net is run
		Then display_value for question_code 1 and result_type "1" is 0.6
		Then display_value for question_code 1 and result_type "2" is 0.4

	Scenario: When net is run with cuts, categorical computations are accurately made
		Given raw 7pt questions results
			| question_code | response | question_type        | respondent_id |
			| 1             | 1        | Categorical_response | 1 |
			| 1             | 1        | Categorical_response | 2 |
			| 1             | 1        | Categorical_response | 3 |
			| 1             | 2        | Categorical_response | 4 |
			| 1             | 2        | Categorical_response | 5 |
			| 2             | 2        | 7pt_1=SA             | 1 |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
			| 4             | Atlanta | Female |
			| 5             | Atlanta | Female |
		When compute net with cut_demographic = region and gender is run
		Then the display_value including region and gender for question_code 1, result_type "1" and region "Atlanta", gender "Female" is 0.5