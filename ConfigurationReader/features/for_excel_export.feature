Feature: When queried for cut menu options, this module provides appropriate list of menus
	Scenario: Basic output for static cuts
		Given basic static cuts
		When cuts_for_excel_menu is run
		Then each cut is represented as an item in a list, starting with title, "static" and all dimension titles

	Scenario: Output cuts for a given menu
		Given basic static cuts with one historical cut
		When cuts_for_excel_menu is run with menu historical
		Then only historical cut is output