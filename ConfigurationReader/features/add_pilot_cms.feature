@wip
Feature: When provided a pilot CM file, add appropriate demographics and cuts
	Scenario: Given a set of pilot ids, create appropriate config cuts
		Given basic static cuts
		When add_pilot_cuts is called with
			| col_1        | col_2       | col_3        |
			| pilot_1      | pilot_1     | pilot_2      |
			| Target Group | All CMs     | Target Group |
			| ignore_line  | ignore_line | ignore_line  |
			| 1            | 1           | 2            |
			|              | 3           |              |
		Then cuts has a cut titled "pilot_1" which has dimensions "pilot_1", "region", and "corps"

	Scenario: Given a set of pilot ids, create appropriate config dimensions
		Given basic static cuts
		When add_pilot_cuts is called with
			| col_1        | col_2       | col_3        |
			| pilot_1      | pilot_1     | pilot_2      |
			| Target Group | All CMs     | Target Group |
			| ignore_line  | ignore_line | ignore_line  |
			| 1            | 1           | 2            |
			|              | 3           |              |
		Then there is a dimension called "pilot_1" that has composite dimensions "pilot_1-Target Group" and "pilot_1-All CMs"