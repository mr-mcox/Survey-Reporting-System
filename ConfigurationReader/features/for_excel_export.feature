Feature: When queried for cut menu options, this module provides appropriate list of menus
	Scenario: Basic output for static cuts
		Given basic static cuts
		When cuts_for_excel_menu is run
		Then each cut is represented as an item in a list, starting with title, "static" and all dimension titles