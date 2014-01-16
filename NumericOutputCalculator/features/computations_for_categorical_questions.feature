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
