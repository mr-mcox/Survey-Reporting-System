@wip
Feature: When provided a pilot CM file, add appropriate demographics and cuts
	Scenario: Given a set of pilot CMs, add labels to the demograhpic table
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
		When add_pilot_cms is called with
			| col_1        | col_2       | col_3        |
			| pilot_1      | pilot_1     | pilot_2      |
			| Target Group | All CMs     | Target Group |
			| ignore_line  | ignore_line | ignore_line  |
			| 1            | 1           | 2            |
			|              | 3           |              |
		Then respondent_id 1 has a value of "Target Group" on "pilot_1-Target Group"
		Then respondent_id 2 has a value of blank on "pilot_1-Target Group"
