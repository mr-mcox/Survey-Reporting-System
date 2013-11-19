Feature: Determine the cuts desired from a configuration file
	Scenario: When a yaml file is loaded with a list of cuts to be used, the reader indicates which columns need to be pulled
		Given input yaml that has one one dimension
		When cuts_to_be_created is called
		Then it returns the cuts in the yaml and an empty cut

	Scenario: When multiple levels are indicated, the full set is included as well as variations with each one of the levels removed
		Given input yaml that has three levels
		When cuts_to_be_created is called
		Then it returns every combination of each of the levels being used or not used