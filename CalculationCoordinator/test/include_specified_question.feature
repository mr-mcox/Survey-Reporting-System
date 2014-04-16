Feature: Only include results for specified questions
Scenario: Only include questions specified
	Given net formatted values
		| respondent_id | question_code | response |
		| 1             | q1             | 1                  |
		| 2             | q1             | 2                  |
		| 3             | q1             | 3                  |
		| 4             | q1             | 4                  |
		| 1             | q2             | 5                  |
		| 2             | q2             | 6                  |
		| 3             | q2             | 7                  |
		| 4             | q2             | 1                  |
	Given demographic data passed to coordinator
		| respondent_id | region  | gender |
		| 1             | Atlanta | Female |
		| 2             | Atlanta | Male   |
		| 3             | SoDak   | Male   |
		| 4             | SoDak   | Female |
	When a config reader that requests national cuts only requests cut for "q2" is assigned
	When compute_cuts_from_config is run
	Then there there is a net entry for question_code "q2"
	Then there there not is a net entry for question_code "q1"