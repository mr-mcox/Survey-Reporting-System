Feature: Compute net/strong/weak/average for all responses on a survey by question

	Scenario: When net formatted values are provided for a question, output net by question
		Given net formatted values
			| question_id | value |
			| 1           | 0     |
			| 1           | 1     |
			| 1           | 1     |
			| 1           | 0     |
			| 1           | -1    |
		When compute net is run
		Then the display_value for question_id 1 is 0.2