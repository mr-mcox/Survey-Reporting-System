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
		Then the net display_value for question_code 1 is 0
		Then the net display_value for question_code 2 is blank
		Then the net display_value for question_code 3 is -0.5
