Feature: Convert fiddler export *.txt files to Python requests script
  As a user
  I want to convert fiddler file to Python requests script
  So that I can use the fd2py tool in tuner
    Background: Some files in directory
        Given I have a fiddler_export1.txt and fiddler_export2.txt in directory
    Scenario: Convert all *.txt in current directory to *.py
        When I run "tuner fd2py"
        Then I should see fiddler_export1.py and fiddler_export1.py in directory
    Scenario: Convert single .txt to *.py
        When I run "tuner fd2py fiddler_export1.txt"
        Then I should see fiddler_export1.py in directory
