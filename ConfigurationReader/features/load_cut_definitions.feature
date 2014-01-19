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
		When a new dimension is created that has the title "Ethnicity"
		Then the new dimension is the same as the original

	Scenario: When a cut is created, it has a title attribute that can later be accessed
		Given basic set of cut and dimensions in config file
		When cuts from the config are accessed
		Then the cuts have titles that they were given in the config

	Scenario: When a dimension is created, it has a title attribute that can later be accessed
		Given basic set of cut and dimensions in config file
		When a new dimension is created that has the title "Ethnicity"
		Then that dimension has a title of "Ethnicity"

	Scenario: All dimensions are returned upon request
		Given basic set of cut and dimensions in config file
		When a new dimension is created that has the title "Ethnicity"
		When a new dimension is created that has the title "Grade"
		Then all_dimensions has dimensions titled "Ethnicity" and "Grade"

	Scenario: Add zero fill when number of levels is less than number of dimensions
		Given input yaml that has one one dimension
		Given that that config has 3 levels by default
		When cuts_to_be_created is called
		Then it returns the cuts in the yaml and an empty cut with two blanks at the end of the list

	Scenario: When a dimension is created, by default it should not have a not included label
		Given basic set of cut and dimensions in config file
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension has a not included label of None

	Scenario: If a not included label is specified, use that in instead
		Given basic set of cut and dimensions in config file with a not included label for ethnicity of "Lack of Ethnicity"
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension has a not included label of "Lack of Ethnicity"

	Scenario: By default, assume that a dimension has a dimension_type of "static"
		Given basic set of cut and dimensions in config file
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension has dimension_type of "static"

	Scenario: If dynamic_parent_dimension is provided than the dimension should have a dimension_type of "dynamic"
		Given basic set of cut and dimensions in config file with a dynamic_parent_dimension for Ethnicity dimension of "Region"
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension has dimension_type of "dynamic"

	Scenario: By default, assume that a dimension has a is_composite flag of False
		Given basic set of cut and dimensions in config file
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension is_composite flag is False

	Scenario: is_composite flag is true if dimension has composite_dimensions
		Given basic set of cut and dimensions in config file with composite dimension for Ethnicity
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension is_composite flag is True

	Scenario: When a composite dimension is involved, create cuts based on each of the components
		Given input yaml that has a composite dimension of "Ethnicity_POC" that includes "ethnicity" and "poc" components
		When cuts_to_be_created is called
		Then it returns cuts with ethnicity and poc

	Scenario: value_order by default returns None
		Given basic set of cut and dimensions in config file with composite dimension for Ethnicity
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension value_order is None

	Scenario: value_order by default returns None
		Given basic set of cut and dimensions in config file with an Ethnicity dimension that has value order of "B" "A"
		When a new dimension is created that has the title "Ethnicity"
		Then the dimension value_order is ["B", "A"]

	Scenario: When multiple dimensions are indicated, the full set of combination is the minimal number of cuts used
		Given input yaml that has two cuts with overlapping dimensions
		When cuts_to_be_created is called
		Then it returns all combinations of cuts
		Then it returns the minimal number of cuts

	Scenario: When a for_historical flag is set, add survey_code to all cuts 
		Given input yaml that has two dimensions, only one of which is historical
		When cuts_to_be_created is called with a for_historical flag
		Then each cut includes the survey_code dimension

	Scenario: When a for_historical flag is set, only return cuts that are listed as being in historical menu
		Given input yaml that has two dimensions, only one of which is historical
		When cuts_to_be_created is called with a for_historical flag
		Then the cuts only include historical cut