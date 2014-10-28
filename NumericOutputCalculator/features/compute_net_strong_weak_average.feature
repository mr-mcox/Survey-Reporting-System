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
	Given raw 7pt questions responses
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
	Given raw 7pt questions responses
		| question_code | response |
		| 1             | 1        |
		| 1             | 1        |
		| 1             | 3        |
		| 1             | 6        |
	When compute net is run
	Then the display_value for question_code 1 is 0.25

Scenario: When 7pt with 1=Strongly Agree questions are given, average is accurately computed
	Given raw 7pt questions responses
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

Scenario: When net formatted values are provided for a question, output strong_count by question
	Given net formatted values
		| question_code | net_formatted_value |
		| 1             | 0                   |
		| 1             | 1                   |
		| 1             | 1                   |
		| 1             | 0                   |
		| 1             | -1                  |
		| 1             |                     |
	When compute strong_count is run
	Then the display_value for question_code 1 is 2

Scenario: When net formatted values are provided for a question, output weak_count by question
	Given net formatted values
		| question_code | net_formatted_value |
		| 1             | 0                   |
		| 1             | 1                   |
		| 1             | 1                   |
		| 1             | 0                   |
		| 1             | -1                  |
		| 1             |                     |
	When compute weak_count is run
	Then the display_value for question_code 1 is 1

Scenario: Compute net formatted values accurately for a variety of question types
	Given raw 7pt questions responses
		| person_id | response | question_type  |
		| 1         | 7        | 7pt_1=SA       |
		| 2         | 3        | 7pt_1=SA       |
		| 3         | 1        | 7pt_1=SA       |
		| 4         | 8        | 7pt_1=SA       |
		| 5         | 10       | 10pt_NPS_1=SA  |
		| 6         | 4        | 10pt_NPS_1=SA  |
		| 7         | 1        | 10pt_NPS_1=SA  |
		| 8         | 11       | 10pt_NPS_1=SA  |
		| 9         | 1        | 7pt_7=SA       |
		| 10        | 5        | 7pt_7=SA       |
		| 11        | 7        | 7pt_7=SA       |
		| 12        | 8        | 7pt_7=SA       |
		| 13        | 11       | 11pt_NPS_1=SA  |
		| 14        | 4        | 11pt_NPS_1=SA  |
		| 15        | 1        | 11pt_NPS_1=SA  |
		| 16        | 12       | 11pt_NPS_1=SA  |
		| 17        | 1        | 10pt_NPS_10=SA |
		| 18        | 7        | 10pt_NPS_10=SA |
		| 19        | 10       | 10pt_NPS_10=SA |
		| 20        | 11       | 10pt_NPS_10=SA |
	When NumericOutputCalculator is initialized
	Then net formatted value for person_id 1 is -1
	Then net formatted value for person_id 2 is 0
	Then net formatted value for person_id 3 is 1
	Then net formatted value for person_id 4 is blank
	Then net formatted value for person_id 5 is -1
	Then net formatted value for person_id 6 is 0
	Then net formatted value for person_id 7 is 1
	Then net formatted value for person_id 8 is blank
	Then net formatted value for person_id 9 is -1
	Then net formatted value for person_id 10 is 0
	Then net formatted value for person_id 11 is 1
	Then net formatted value for person_id 12 is blank
	Then net formatted value for person_id 13 is -1
	Then net formatted value for person_id 14 is 0
	Then net formatted value for person_id 15 is 1
	Then net formatted value for person_id 16 is blank
	Then net formatted value for person_id 17 is -1
	Then net formatted value for person_id 18 is 0
	Then net formatted value for person_id 19 is 1
	Then net formatted value for person_id 20 is blank

Scenario: Compute net formatted values accurately for a variety of question types
	Given raw 7pt questions responses
		| person_id | response | question_type  |
		| 1         | 7        | 7pt_1=SA       |
		| 2         | 3        | 7pt_1=SA       |
		| 3         | 1        | 7pt_1=SA       |
		| 4         | 8        | 7pt_1=SA       |
		| 5         | 10       | 10pt_NPS_1=SA  |
		| 6         | 4        | 10pt_NPS_1=SA  |
		| 7         | 1        | 10pt_NPS_1=SA  |
		| 8         | 11       | 10pt_NPS_1=SA  |
		| 9         | 1        | 7pt_7=SA       |
		| 10        | 5        | 7pt_7=SA       |
		| 11        | 7        | 7pt_7=SA       |
		| 12        | 8        | 7pt_7=SA       |
		| 13        | 11       | 11pt_NPS_1=SA  |
		| 14        | 4        | 11pt_NPS_1=SA  |
		| 15        | 1        | 11pt_NPS_1=SA  |
		| 16        | 12       | 11pt_NPS_1=SA  |
		| 17        | 1        | 10pt_NPS_10=SA |
		| 18        | 7        | 10pt_NPS_10=SA |
		| 19        | 10       | 10pt_NPS_10=SA |
		| 20        | 11       | 10pt_NPS_10=SA |
	When NumericOutputCalculator is initialized
	Then the response value for person_id 1 is 1
	Then the response value for person_id 2 is 5
	Then the response value for person_id 3 is 7
	Then the response value for person_id 4 is blank
	Then the response value for person_id 5 is 1
	Then the response value for person_id 6 is 7
	Then the response value for person_id 7 is 10
	Then the response value for person_id 8 is blank
	Then the response value for person_id 9 is 1
	Then the response value for person_id 10 is 5
	Then the response value for person_id 11 is 7
	Then the response value for person_id 12 is blank
	Then the response value for person_id 13 is 0
	Then the response value for person_id 14 is 7
	Then the response value for person_id 15 is 10
	Then the response value for person_id 16 is blank
	Then the response value for person_id 17 is 1
	Then the response value for person_id 18 is 7
	Then the response value for person_id 19 is 10
	Then the response value for person_id 20 is blank


Scenario: Compute net formatted values accurately for NPS 11 = SA
	Given raw 7pt questions responses
		| person_id | response | question_type  |
		| 17        | 1        | 11pt_NPS_11=SA |
		| 18        | 9        | 11pt_NPS_11=SA |
		| 19        | 11       | 11pt_NPS_11=SA |
		| 20        | 12       | 11pt_NPS_11=SA |
	When NumericOutputCalculator is initialized
	Then net formatted value for person_id 17 is -1
	Then net formatted value for person_id 18 is 0
	Then net formatted value for person_id 19 is 1
	Then net formatted value for person_id 20 is blank
