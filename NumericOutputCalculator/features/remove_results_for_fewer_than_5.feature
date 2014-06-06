Feature: Remove results when the question is confidential and there are fewere than 5 respondents
	Scenario: Remove display values for fewer than 5
		Given net formatted values
			| question_code | net_formatted_value | is_confidential |
			| 1             | 0                   | 1               |
			| 1             | 1                   | 1               |
			| 1             | -1                  | 1               |
			| 1             | 0                   | 1               |
			| 1             | 0                   | 1               |
			| 2             | -1                  | 1               |
			| 2             | 0                   | 1               |
			| 3             | -1                  | 0               |
			| 3             | 0                   | 0               |
		When compute net is run
		Then the "net" display_value for question_code "1" is 0
		Then the "net" display_value for question_code "2" is blank
		Then the "net" display_value for question_code "3" is -0.5

	Scenario: Retain sample sizes for confidential questions
		Given net formatted values
			| question_code | net_formatted_value | is_confidential |
			| 1             | 0                   | 1               |
			| 1             | 1                   | 1               |
			| 1             | -1                  | 1               |
			| 1             | 0                   | 1               |
			| 1             | 0                   | 1               |
			| 2             | -1                  | 1               |
			| 2             | 0                   | 1               |
			| 3             | -1                  | 0               |
			| 3             | 0                   | 0               |
		When compute sample size is run
		Then the "sample_size" display_value for question_code "2" is 2


	Scenario: Remove display values for fewer than 5 when only one dimension of a cut would be affected
		Given net formatted values
			| question_code | net_formatted_value | is_confidential | respondent_id |
			| 1             | 0                   | 1               | 1             |
			| 1             | 1                   | 1               | 2             |
			| 1             | -1                  | 1               | 3             |
			| 1             | 0                   | 1               | 4             |
			| 1             | 0                   | 1               | 5             |
			| 1             | -1                  | 1               | 6             |
			| 1             | 0                   | 1               | 7             |
		Given demographic data
			| respondent_id | region  |
			| 1             | Atlanta |
			| 2             | Atlanta |
			| 3             | Atlanta |
			| 4             | Atlanta |
			| 5             | Atlanta |
			| 6             | SoDak   |
			| 7             | SoDak   |
		When compute net with cut_demographic = region is run
		Then the regional "net" display_value for question_code "1" and region "Atlanta" is 0
		Then the regional "net" display_value for question_code "1" and region "SoDak" is blank

	Scenario: Remove display values for fewer than 5 for categorical responses
		Given raw 7pt questions results
			| question_code | response | question_type        | respondent_id | is_confidential |
			| 1             | 1        | Categorical_response | 1             | 1               |
			| 1             | 1        | Categorical_response | 2             | 1               |
			| 1             | 1        | Categorical_response | 3             | 1               |
			| 1             | 2        | Categorical_response | 4             | 1               |
			| 2             | 2        | 7pt_1=SA             | 1             | 1               |
		Given demographic data
			| respondent_id | region  |
			| 1             | Atlanta |
			| 2             | Atlanta |
			| 3             | Atlanta |
			| 4             | Atlanta |
			| 5             | Atlanta |
			| 6             | SoDak   |
			| 7             | SoDak   |
		When compute net is run
		Then display_value for question_code 1 and result_type "1" is blank
