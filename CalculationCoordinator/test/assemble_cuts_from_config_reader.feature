Feature: When provided a config reader, the calculation coordinator can create the calculations specified
	Scenario: Given a set of cuts from config reader, the calculation coordinator computes the cuts given
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
			| 4             | 1             | -1                  |
		Given demographic data passed to coordinator
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Male   |
			| 3             | SoDak   | Male   |
			| 4             | SoDak   | Female |
		Given a config reader that returns ["region","gender"] and ["region",None]
		Given the config reader has 2 levels by default
		When compute_cuts_from_config is run
		Then master_aggregation row_headers has six rows