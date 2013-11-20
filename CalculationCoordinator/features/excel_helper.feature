Feature: A few helper fuctions for exporting excel data
	Scenario: When given a row and column with a start index of 0, convert that to a range string
		Given a CalculationCoordinator object
		When rc_to_range is called with input of row = 2 and col = 3
		Then the return is 'D3'

	Scenario: When a range is indicated, return the range as a string
		Given a CalculationCoordinator object
		When rc_to_range is called with input of row = 2, col = 3, height = 3, width = 2
		Then the return is 'D3:E5'