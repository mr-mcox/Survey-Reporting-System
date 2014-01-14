Feature: As a report creator writing reports, in order to see results faster I want to be able to set a flag so that statistical significance is not computed
	Scenario: When the no_stat_significance_computations flag is set, calls to stat signficance are made with no_stat_significance_computation = True
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1             | 1                   |
			| 2             | 1             | 0                   |
			| 3             | 1             | -1                  |
			| 4             | 1             | -1                  |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Male   |
			| 3             | SoDak   | Male   |
			| 4             | SoDak   | Female |
		Given a config reader that returns ["region","gender"] and ["region",None] and the no_stat_significance_computation flag set
		When compute_significance_from_config is run
		Then bootstrap_net_significance is called with no_stat_significance_computation = True