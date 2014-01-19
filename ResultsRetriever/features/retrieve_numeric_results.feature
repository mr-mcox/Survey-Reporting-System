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
		Given a question table with this data
			| id | question_code |
			| 1  | CSI1          |
			| 2  | CSI2          |
			| 3  | CSI3          |
			| 4  | CSI4          |
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
		Given a question table with this data
			| id | question_code |
			| 1  | CSI1          |
			| 2  | CSI2          |
			| 3  | CSI3          |
			| 4  | CSI4          |
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
			| 1  | 1314F8W     |
			| 2  | 1314MYS     |
		Given a question table with this data
			| id | question_code |
			| 1  | CSI1          |
			| 2  | CSI2          |
			| 3  | CSI3          |
			| 4  | CSI4          |
		When retrieve results for survey_code 1314F8W is run
		Then there are 8 rows returned

	Scenario: Retrieve question code with results rather than question_id
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
			| 1  | 1314F8W     |
			| 2  | 1314MYS     |
		Given a question table with this data
			| id | question_code |
			| 1  | CSI1          |
			| 2  | CSI2          |
			| 3  | CSI3          |
			| 4  | CSI4          |
		When retrieve results for survey_code 1314F8W is run
		Then there are 8 rows returned
		Then one of the columns returned is question_code

	Scenario: Return is_confidential column
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
			| 1  | 1314F8W     |
			| 2  | 1314MYS     |
		Given a question table with this data
			| id | question_code | is_confidential |
			| 1  | CSI1          | 1               |
			| 2  | CSI2          | 1               |
			| 3  | CSI3          | 1               |
			| 4  | CSI4          | 1               |
		When retrieve results for survey_code 1314F8W is run
		Then one of the columns returned is is_confidential

	Scenario: Return question_type column
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
			| 1  | 1314F8W     |
			| 2  | 1314MYS     |
		Given a question table with this data
			| id | question_code | is_confidential | question_type |
			| 1  | CSI1          | 1               | 7pt_1=SA      |
			| 2  | CSI2          | 1               | 7pt_1=SA      |
			| 3  | CSI3          | 1               | 7pt_1=SA      |
			| 4  | CSI4          | 1               | 7pt_1=SA      |
		When retrieve results for survey_code 1314F8W is run
		Then one of the columns returned is question_type

	Scenario: Retrieve results for multiple surveys
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
			| 1  | 1314F8W     |
			| 2  | 1314MYS     |
		Given a question table with this data
			| id | question_code |
			| 1  | CSI1          |
			| 2  | CSI2          |
			| 3  | CSI3          |
			| 4  | CSI4          |
		When retrieve results for multiple surveys with survey_code 1314F8W and 1314MYS is run
		Then there are 10 rows returned
