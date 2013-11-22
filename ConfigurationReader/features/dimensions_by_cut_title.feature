Feature: As an excel assembler, in order to easily output data for a survey, I want a list of the order of columns given with the inforomation that was used to store the calculation
	Scenario: When dimensions by cuts is requested from the configuration reader, a dict of all cuts with a list of Dimension objects in the order that they should be displayed is returned
		Given a configuration reader object with a set of cuts organized into dimensions
		When columns_for_row_header is called
		Then a list of dicts with result_type, columns_used is returned