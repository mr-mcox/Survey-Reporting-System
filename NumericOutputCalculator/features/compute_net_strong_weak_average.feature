Feature: Compute net/strong/weak/average for all responses on a survey by question

	Scenario: When net formatted values are provided for a question, output net by question
		Given net formatted values
			| question_id | value |
			| 1           | 0     |
			| 1           | 1     |
			| 1           | 1     |
			| 1           | 0     |
			| 1           | -1    |
			| 1           |       |
		When compute net is run
		Then the display_value for question_id 1 is 0.2

	Scenario: When net formatted values are provided for a question, output strong by question
		Given net formatted values
			| question_id | value |
			| 1           | 0     |
			| 1           | 1     |
			| 1           | 1     |
			| 1           | 0     |
			| 1           | -1    |
			| 1           |       |
		When compute strong is run
		Then the display_value for question_id 1 is 0.4

Scenario: When net formatted values are provided for a question, output weak by question
		Given net formatted values
			| question_id | value |
			| 1           | 0     |
			| 1           | 1     |
			| 1           | 1     |
			| 1           | 0     |
			| 1           | -1    |
			| 1           |       |
		When compute weak is run
		Then the display_value for question_id 1 is 0.2

Scenario: When net formatted values are provided for multiple questions, output net by question
		Given net formatted values
			| question_id | value |
			| 1           | 0     |
			| 1           | 1     |
			| 1           | 1     |
			| 1           | 0     |
			| 2           | -1    |
			| 2           |       |
		When compute net is run
		Then the display_value for question_id 1 is 0.5
		Then the display_value for question_id 2 is -1