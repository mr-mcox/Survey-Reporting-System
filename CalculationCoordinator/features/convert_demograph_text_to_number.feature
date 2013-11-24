Feature: In order to allow any text to be used in cutting yet maintain sane sorting in excel, all demographics text should be converted to numbers

	Scenario: When multiple cuts are run, they are stored by tuple
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1           | 1     |
			| 2             | 1           | 0     |
			| 3             | 1           | -1    |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male |
		When compute net with cut_demographic = region and gender is run
		When compute net with cut_demographic = region is run
		Then computations_generated has a length of 2
		Then the display_value including region for question_code 1 and region "Atlanta" is 0.5

	Scenario: Identify all demographic columns across multiple cuts
		Given computations generated that include a cut by gender and a cut by region
		When replace_dimensions_with_integers is run
		Then columns of computations_generated are strings with filled numbers
		Then same number of unique values in dimension columns exists before and after

	Scenario: Identify all demographic columns across multiple cuts when there are the same values across multiple cuts
		Given computations generated that include a cut by gender and a cut by region with duplicates
		When replace_dimensions_with_integers is run
		Then columns of computations_generated are strings with filled numbers
		Then same number of unique values in dimension columns exists before and after

	Scenario: After changing all dimensions to numbers, we have a mapping that we can re-assemble the cuts with
		Given computations generated that include a cut by gender and a cut by region with duplicates
		When replace_dimensions_with_integers is run
		Then there is a mapping of the values back to numbers

	Scenario: Mapping is sorted by integer string so that excel doesn't need to re-sort
		Given computations generated that include a cut by gender and a cut by region with duplicates
		When replace_dimensions_with_integers is run
		Then the mapping is in order by integer strings
		Then the values column corresponds with the appropriate integer strings

	Scenario: CalcCoordinator computes multiple result types at the same time
		Given net formatted values
			| respondent_id | question_code | net_formatted_value |
			| 1             | 1           | 1     |
			| 2             | 1           | 0     |
			| 3             | 1           | -1    |
		Given demographic data
			| respondent_id | region  | gender |
			| 1             | Atlanta | Female |
			| 2             | Atlanta | Female |
			| 3             | SoDak   | Male |
		Given CalcCoordinator result types of net, strong and weak
		When compute net with cut_demographic = region is run
		Then result_type of results includes net, strong and weak