Feature: Compute sample size
	Scenario: Compute basic sample size for questions
		Given raw 7pt questions responses
			| question_code | response |
			| 1             | 1        |
			| 1             | 2        |
			| 1             | 3        |
			| 1             | 1        |
			| 2             | 2        |
			| 2             |          |
		When compute sample size is run
		Then the display_value for question_code 1 is 4
		Then the display_value for question_code 2 is 1
