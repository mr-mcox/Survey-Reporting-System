Feature: As an excel assembler, in order to easily output data for a survey, I want a list of all dimensions used by cuts
	Scenario: When dimensions by cuts is requested from the configuration reader, a dict of all cuts with a list of Dimension objects in the order that they should be displayed is returned
		Given a configuration reader object with a set of cuts organized into dimensions
		When dimensions_by_cuts is called
		Then a dict of all cuts with Dimension objects is returned