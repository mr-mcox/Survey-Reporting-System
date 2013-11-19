Feature: Determine the cuts desired from a configuration file
	Scenario: When a yaml file is loaded with a list of cuts to be used, the reader indicates which columns need to be pulled
		Given input yaml that has one one dimension
		When cuts_to_be_created is called
		Then it returns the cuts in the yaml and an empty cut