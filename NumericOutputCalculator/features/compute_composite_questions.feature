Feature: Accurately compute composite questions like Net Corps Strength and Net Corps Learning
	Scenario: Compute composite question results for strong percent
		Given net formatted values
			| question_code | net_formatted_value |
			| q1             | 0                   |
			| q1             | 1                   |
			| q1             | 1                   |
			| q2             | 1                   |
			| q2             | -1                  |
			| q2             | 1                   |
			| q3             | 0                   |
			| q3             | -1                  |
			| q3             | 0                   |
		When compute net is run with composite of NQ is q1 and q2
		Then the display_value for string based question_code NQ is 0.5

	Scenario: Compute composite question results for strong percent and demographics
		Given net formatted values
			| question_code | net_formatted_value | respondent_id |
			| q1             | 0                   | 1 |
			| q1             | 1                   | 2 |
			| q1             | 1                   | 3 |
			| q2             | 1                   | 1 |
			| q2             | -1                  | 2 |
			| q2             | 1                   | 3 |
			| q3             | 0                   | 1 |
			| q3             | -1                  | 2 |
			| q3             | 0                   | 3 |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
		When compute net is run with composite of NQ is q1 and q2 and region cut
		Then the regional display_value for string based question_code NQ and region "Atlanta" is 0.25

	Scenario: Compute composite question results for strong count
		Given net formatted values
			| question_code | net_formatted_value |
			| q1             | 0                   |
			| q1             | 1                   |
			| q1             | 1                   |
			| q2             | 1                   |
			| q2             | -1                  |
			| q2             | 0                   |
			| q3             | 0                   |
			| q3             | -1                  |
			| q3             | 0                   |
		When compute strong_count is run with composite of NQ is q1 and q2
		Then the display_value for string based question_code NQ is 1.5

	Scenario: Compute composite question results for sample_size count
		Given net formatted values
			| question_code | net_formatted_value |
			| q1             | 0                   |
			| q1             | 1                   |
			| q1             | 1                   |
			| q2             | 1                   |
			| q2             | -1                  |
			| q2             | 0                   |
			| q3             | 0                   |
			| q3             | -1                  |
			| q3             | 0                   |
		When compute sample_size is run with composite of NQ is q1 and q2
		Then the display_value for string based question_code NQ is 3

	Scenario: When composite questions are confidential, composite question should be blank when sample size is small
		Given net formatted values
			| question_code | net_formatted_value | is_confidential |
			| q1             | 0                   | 1 |
			| q1             | 1                   | 1 |
			| q1             | 1                   | 1 |
			| q2             | 1                   | 1 |
			| q2             | -1                  | 1 |
			| q2             | 0                   | 1 |
			| q3             | 0                   | 1 |
			| q3             | -1                  | 1 |
			| q3             | 0                   | 1 |
		When compute net is run with composite of NQ is q1 and q2
		Then the display_value for string based question_code NQ is blank

	Scenario: When composite questions are confidential and cut for demographics is used, composite question should be blank when sample size is small
		Given net formatted values
			| question_code | net_formatted_value | respondent_id | is_confidential |
			| q1             | 0                   | 1 | 1 |
			| q1             | 1                   | 2 | 1 |
			| q1             | 1                   | 3 | 1 |
			| q2             | 1                   | 1 | 1 |
			| q2             | -1                  | 2 | 1 |
			| q2             | 1                   | 3 | 1 |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
		When compute net is run with composite of NQ is q1 and q2 and region cut
		Then the regional display_value for string based question_code NQ and region "Atlanta" is blank


	Scenario: When composite questions are not confidential, composite question should be not be blank when sample size is small
		Given net formatted values
			| question_code | net_formatted_value | is_confidential |
			| q1             | 0                   | 0 |
			| q1             | 1                   | 0 |
			| q1             | 1                   | 0 |
			| q2             | 1                   | 0 |
			| q2             | -1                  | 0 |
			| q2             | 1                   | 0 |
			| q3             | 0                   | 1 |
			| q3             | -1                  | 1 |
			| q3             | 0                   | 1 |
		When compute net is run with composite of NQ is q1 and q2
		Then the net display_value for string based question_code NQ is 0.5

