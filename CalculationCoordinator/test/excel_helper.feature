Feature: A few helper fuctions for exporting excel data
	Scenario: When given a row and column with a start index of 0, convert that to a range string
		Given a generic coordinator
		Then the result of rc_to_range with row = 2 and col = 3 is "D3"

	Scenario: When a range is indicated, return the range as a string
		Given a generic coordinator
		Then the result of rc_to_range with row = 2, col = 3, height = 3, width = 2 is "D3:E5"
