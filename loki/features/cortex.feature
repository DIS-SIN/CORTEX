Feature: Evalhalla
  Thank you for taking part in this survey. The results of this survey
  will be used to demonstrate how Evalhalla can be used
  to quickly collect valuable data and provide instant access to survey results
  through a real-time dashboard for immediate consumption.
  Please take a few minutes to answer the following questions.

  Scenario: Sending and receiving survey in evalese format
     Given "designer" creates "test_sur" in "evalese" format
      When "designer" sends "test_sur" in "evalese" via "survey_evalese" to Yggdrasil
      Then "player" receives "test_sur" in "evalese" via "survey_evalese" from Yggdrasil
