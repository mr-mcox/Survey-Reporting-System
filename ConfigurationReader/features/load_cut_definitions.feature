Feature: Determine the cuts desired from a configuration file
	Scenario: When a yaml file is loaded with a list of cuts to be used, the reader indicates which columns need to be pulled
		Given input yaml that has one one dimension
		When cuts_to_be_created is called
		Then it returns the cuts in the yaml and an empty cut

	Scenario: When multiple dimensions are indicated, the full set is included as well as variations with each one of the dimensions removed
		Given input yaml that has three dimensions
		When cuts_to_be_created is called
		Then it returns every combination of each of the dimensions being used or not used

	Scenario: Given a basic set of cuts with dimensions and dimensions, a cut object is created for each cut in the input
		Given basic set of cut and dimensions in config file
		When cuts from the config are accessed
		Then the number of cut objects equal to the number of cuts in the config are returned

	Scenario: When a cut object is created, it creates dimension objects equal corresponding to dimension in the config passed to it
		Given a cut object with config information
		When the cut object is created
		Then it has dimension objects that correspond to the dimensions in the config object

	Scenario: Dimensions are re-used from master list if they are already available
		Given a dimension list with a dimension named "Ethnicity"
		When a new dimension is created that has the title ethnicity
		Then the new dimension is the same as the original