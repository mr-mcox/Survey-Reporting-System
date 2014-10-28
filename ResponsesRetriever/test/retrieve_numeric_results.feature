Feature: Retreive all responses from a single survey from a database
Scenario: Retrieve all responses from a survey by name
		Given set up database schema
		Given two survey db
		When retrieve responses for survey_code 1314F8W is run
		Then there are 8 rows returned

	Scenario: Retrieve question code with responses rather than question_id
		Given set up database schema
		Given two survey db
		When retrieve responses for survey_code 1314F8W is run
		Then there are 8 rows returned
		Then one of the columns returned is question_code

	Scenario: Return is_confidential column
		Given set up database schema
		Given two survey db
		When retrieve responses for survey_code 1314F8W is run
		Then one of the columns returned is is_confidential

	Scenario: Return question_type column
		Given set up database schema
		Given two survey db
		When retrieve responses for survey_code 1314F8W is run
		Then one of the columns returned is question_type

	Scenario: Retrieve responses for multiple surveys
		Given set up database schema
		Given two survey db
		When retrieve responses for multiple surveys with survey_code 1314F8W and 1314MYS is run
		Then there are 10 rows returned

	Scenario: Include survey_code in result output if there is more than one survey listed
		Given set up database schema
		Given two survey db
		When retrieve responses for multiple surveys with survey_code 1314F8W and 1314MYS is run
		Then one of the columns returned is survey_code