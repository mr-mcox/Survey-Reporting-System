Feature: Export cuts in files for further analysis
	Scenario: Given a set of cuts from config reader, the calculation coordinator computes the cuts given
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
			| 4             | 1             | -1                  |
		Given demographic data passed to coordinator
			| respondent_id | region  | gender |
			| 1             | Atlanta | Male   |
			| 2             | Atlanta | Male   |
			| 3             | SoDak   | Male   |
			| 4             | SoDak   | Female |
		Given a config reader that returns ["region","gender"]
		When export_cuts_to_files is run
		Then there is a csv file named "cut_1.csv" that has region and gender columns