Feature: Compute statistical significance via bootstrapping

	Scenario: When aggregations_for_net_significance is called for a set of cuts, it makes appropriate calls to aggregation_computation
		Given a generic NumericOutputCalculator
		When aggregations_for_net_significance is called for cut ["ethnicity","region","corps"]
		Then compute_aggregation is called for cuts ["ethnicity","region","corps"] and result_type ["sample_size","strong_count","weak_count"]
		Then compute_aggregation is called for cuts ["region","corps"] and result_type ["sample_size","strong_count","weak_count"]

	Scenario: When aggregations_for_net_significance is called for one dimension, it calls aggregation_computation with no cuts
		Given a generic NumericOutputCalculator
		When aggregations_for_net_significance is called for cut ["region"]
		Then compute_aggregation is called for cuts ["region"] and result_type ["sample_size","strong_count","weak_count"]
		Then compute_aggregation is called for cuts [] and result_type ["sample_size","strong_count","weak_count"]

	Scenario: Generate table of counts to be used for computation
		Given raw 7pt questions results
				| respondent_id | question_code | response |
				| 1             | 1             | 1        |
				| 2             | 1             | 3        |
				| 3             | 1             | 7        |
				| 4             | 1             | 1        |
				| 5             | 1             | 7        |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
			| 4             | SoDak   | Male   |
			| 5             | SoDak   | Female |
		When bootstrap_net_significance is called for cut ["gender","region"]
		Then count for region "SoDak" gender "Male" and column "weak_count" is 1
		Then count for region "SoDak" gender "Male" and column "comp_weak_count" is 2

	Scenario: Generate table of counts to be used for computation even when there is only one cut
		Given raw 7pt questions results
				| respondent_id | question_code | response |
				| 1             | 1             | 1        |
				| 2             | 1             | 7        |
				| 3             | 1             | 7        |
				| 4             | 1             | 1        |
				| 5             | 1             | 7        |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male   |
			| 4             | SoDak   | Male   |
			| 5             | SoDak   | Female |
		When bootstrap_net_significance is called for cut ["region"]
		Then count for region "SoDak" and column "weak_count" is 2
		Then count for region "SoDak" and column "comp_weak_count" is 3

	Scenario: When provided a frequency table, return a series of reasonable significance values
		Given statistical significance frequency table for cut region and gender
			| region  | gender | sample_size | strong_count | weak_count | comp_sample_size | comp_strong_count | comp_weak_count | question_code |
			| Atlanta | Male   | 100         | 70           | 10         | 200              | 100               | 20              | 1             |
			| Atlanta | Female | 100         | 30           | 10         | 200              | 100               | 20              | 1             |
			| SoDak   | Male   | 3           | 2            | 0          | 15               | 12                | 3               | 1             |
		When bootstrap_result_from_frequency_table is run
		Then aggregation_value for region "Atlanta" and gender "Male" is "H"
		Then aggregation_value for region "Atlanta" and gender "Female" is "L"
		Then aggregation_value for region "SoDak" and gender "Male" is "S"
