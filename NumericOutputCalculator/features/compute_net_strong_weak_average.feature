Feature: Compute net/strong/weak/average for all responses on a survey by question

	Scenario: When net formatted values are provided for a question, output net by question
		Given net formatted values
			| question_code | net_formatted_value |
			| 1             | 0                   |
			| 1             | 1                   |
			| 1             | 1                   |
			| 1             | 0                   |
			| 1             | -1                  |
			| 1             |                     |
		When compute net is run
		Then the display_value for question_code 1 is 0.2

	Scenario: When net formatted values are provided for a question, output strong by question
		Given net formatted values
			| question_code | net_formatted_value |
			| 1             | 0                   |
			| 1             | 1                   |
			| 1             | 1                   |
			| 1             | 0                   |
			| 1             | -1                  |
			| 1             |                     |
		When compute strong is run
		Then the display_value for question_code 1 is 0.4

Scenario: When net formatted values are provided for a question, output weak by question
		Given net formatted values
			| question_code | net_formatted_value |
			| 1             | 0                   |
			| 1             | 1                   |
			| 1             | 1                   |
			| 1             | 0                   |
			| 1             | -1                  |
			| 1             |                     |
		When compute weak is run
		Then the display_value for question_code 1 is 0.2

Scenario: When net formatted values are provided for multiple questions, output net by question
		Given net formatted values
			| question_code | net_formatted_value |
			| 1             | 0                   |
			| 1             | 1                   |
			| 1             | 1                   |
			| 1             | 0                   |
			| 2             | -1                  |
			| 2             |                     |
		When compute net is run
		Then the display_value for question_code 1 is 0.5
		Then the display_value for question_code 2 is -1

Scenario: When 7pt with 1=Strongly Agree questions are given, net formatted values are appropriately computed
	Given raw 7pt questions results
		| person_id | response |
		| 1         | 7        |
		| 2         | 6        |
		| 3         | 5        |
		| 4         | 4        |
		| 5         | 3        |
		| 6         | 2        |
		| 7         | 1        |
		| 8         | 8        |
	When NumericOutputCalculator is initialized
	Then net formatted value for person_id 1 is -1
	Then net formatted value for person_id 2 is -1
	Then net formatted value for person_id 3 is -1
	Then net formatted value for person_id 4 is -1
	Then net formatted value for person_id 5 is 0
	Then net formatted value for person_id 6 is 1
	Then net formatted value for person_id 7 is 1
	Then net formatted value for person_id 8 is blank

Scenario: When 7pt with 1=Strongly Agree questions are given, net is accurately computed
	Given raw 7pt questions results
		| question_code | response |
		| 1             | 1        |
		| 1             | 1        |
		| 1             | 3        |
		| 1             | 6        |
	When compute net is run
	Then the display_value for question_code 1 is 0.25

Scenario: When 7pt with 1=Strongly Agree questions are given, average is accurately computed
	Given raw 7pt questions results
		| question_code | response |
		| 1             | 1        |
		| 1             | 1        |
		| 1             | 3        |
		| 1             | 7        |
	When compute average is run
	Then the display_value for question_code 1 is 3

Scenario: When cut is created, it should include the type of result
	Given net formatted values
			| question_code | net_formatted_value |
			| 1             | 0                   |
			| 1             | 1                   |
			| 1             | 1                   |
			| 1             | 0                   |
			| 2             | -1                  |
			| 2             |                     |
	When compute net is run
	Then there is a result_type column where all rows have value of net

Scenario: When multiple result types are specified, output has all of them
	Given net formatted values
			| question_code | net_formatted_value |
			| 1             | 0                   |
			| 1             | 1                   |
			| 1             | 1                   |
			| 1             | 0                   |
			| 2             | -1                  |
			| 2             |                     |
	When when compute_aggregation is run with net and strong
	Then there is a result_type column that include both net and strong