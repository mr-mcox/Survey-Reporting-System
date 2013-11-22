Feature: Upon request, provide a mapping from label to integer string
	Scenario: A basic mapping is returned when a dimension is provided
		Given a CalculationCoordinator integer label mapping
		When get_integer_string_mapping with "Gender" is called
		Then a dict with two arrays that correspond to the integers and labels for Gender are returned