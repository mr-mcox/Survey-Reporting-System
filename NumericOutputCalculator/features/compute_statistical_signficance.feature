Feature: Compute statistical significance via bootstrapping

	Scenario: When bootstrap_net_significance is called for a set of cuts, it makes appropriate calls to aggregation_computation
		Given a generic NumericOutputCalculator
		When bootstrap_net_significance is called for cut ["ethnicity","region","corps"]
		Then compute_aggregation is called for cuts ["ethnicity","region","corps"] and result_type ["sample_size","strong_count","weak_count"]
		Then compute_aggregation is called for cuts ["region","corps"] and result_type ["sample_size","strong_count","weak_count"]

	Scenario: When bootstrap_net_significance is called for one dimension, it calls aggregation_computation with no cuts
		Given a generic NumericOutputCalculator
		When bootstrap_net_significance is called for cut ["region"]
		Then compute_aggregation is called for cuts ["region"] and result_type ["sample_size","strong_count","weak_count"]
		Then compute_aggregation is called for cuts [] and result_type ["sample_size","strong_count","weak_count"]