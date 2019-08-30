Feature: Evalhalla
  Thank you for taking part in this survey. The results of this survey
  will be used to demonstrate how Evalhalla can be used
  to quickly collect valuable data and provide instant access to survey results
  through a real-time dashboard for immediate consumption.
  Please take a few minutes to answer the following questions.

  Scenario: Sending and receiving survey in evalese format
     Given "valhalla designer" creates "TEST_SUR" in "evalese" format
      When "valhalla designer" sends "TEST_SUR" in "evalese" format via "survey_evalese" to Yggdrasil
      Then "player" receives "TEST_SUR" in "evalese" format via "survey_evalese" from Yggdrasil

  Scenario: Sending and receiving survey in template format
     Given "valhalla designer" creates "TEST_SUR" in "template" format
      When "valhalla designer" sends "TEST_SUR" in "template" format via "survey_template" to Yggdrasil
      Then "jotunheimr" receives "TEST_SUR" in "template" format from "valhalla designer"
      And it creates a "Valhalla_Survey" and "15" of "Valhalla_Question"
