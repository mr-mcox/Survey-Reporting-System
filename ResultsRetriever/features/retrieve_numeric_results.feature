Feature: Retreive all results from a single survey from a database
	Scenario: Retrieve all results from a survey when there is only one survey
		Given set up database schema
		Given a results table with this data
			| respondent_id | survey_id | question_id | response |
			| 1             | 1         | 1           | 5        |
			| 1             | 1         | 2           | 5        |
			| 1             | 1         | 3           | 5        |
			| 1             | 1         | 4           | 5        |
			| 2             | 1         | 1           | 5        |
			| 2             | 1         | 2           | 5        |
			| 2             | 1         | 3           | 5        |
			| 2             | 1         | 4           | 5        |
		When retrieve results for survey_id 1 is run
		Then there are 8 rows returned

	Scenario: Retrieve all results from a survey when there is more than one survey
		Given set up database schema
		Given a results table with this data
			| respondent_id | survey_id | question_id | response |
			| 1             | 1         | 1           | 5        |
			| 1             | 1         | 2           | 5        |
			| 1             | 1         | 3           | 5        |
			| 1             | 1         | 4           | 5        |
			| 2             | 1         | 1           | 5        |
			| 2             | 1         | 2           | 5        |
			| 2             | 1         | 3           | 5        |
			| 2             | 1         | 4           | 5        |
			| 1             | 2         | 1           | 5        |
			| 1             | 2         | 2           | 5        |
		When retrieve results for survey_id 1 is run
		Then there are 8 rows returned

	Scenario: Retrieve all results from a survey by name
		Given set up database schema
		Given a results table with this data
			| respondent_id | survey_id | question_id | response |
			| 1             | 1         | 1           | 5        |
			| 1             | 1         | 2           | 5        |
			| 1             | 1         | 3           | 5        |
			| 1             | 1         | 4           | 5        |
			| 2             | 1         | 1           | 5        |
			| 2             | 1         | 2           | 5        |
			| 2             | 1         | 3           | 5        |
			| 2             | 1         | 4           | 5        |
			| 1             | 2         | 1           | 5        |
			| 1             | 2         | 2           | 5        |
		Given a survey table with this data
			| id | survey_code |
			| 1 | 1314F8W |
			| 2 | 1314MYS |
		When retrieve results for survey_code 1314F8W is run
		Then there are 8 rows returned