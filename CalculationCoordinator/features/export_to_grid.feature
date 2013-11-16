Feature: Take set of calculations and turn into a sorted grid for excel to consume

	Scenario: Set column and row headers
		Given a set of calculations generated with region and gender and with integer labels
		When create row and column headers is run
		Then each calcualation table has row and column header columns
		Then the column header consists of question and result type joined by a "."
		Then the row header consists of either gender or region