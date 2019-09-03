Feature: Evalhalla
  Thank you for taking part in this survey. The results of this survey
  will be used to demonstrate how Evalhalla can be used
  to quickly collect valuable data and provide instant access to survey results
  through a real-time dashboard for immediate consumption.
  Please take a few minutes to answer the following questions.

  Scenario: Sending and receiving survey in evalese format
     Given valhalla designer creates "TEST_SUR" in "evalese" format
      When valhalla designer sends it via "survey_evalese" to Yggdrasil
      Then valhalla player receives it from Yggdrasil

  Scenario: Sending and receiving survey in template format
     Given valhalla designer creates "TEST_SUR" in "template" format
      When valhalla designer sends it via "survey_template" to Yggdrasil
      Then jotunheimr receives it and creates a "Valhalla_Survey" with a number of "Valhalla_Question"

  Scenario: Sending and receiving a number of survey responses
     Given valhalla player creates from "0" to "1" "TEST_SUR" "responses" in "survey_response" format
      When valhalla player sends them via "survey_response" to Yggdrasil
      Then jotunheimr receives them and creates a number of "Valhalla_Response" with "Valhalla_Respondent" and "Valhalla_Answer"

  Scenario: Receiving free text answers and producing sentiment values
    Given "asgard" receives free text answers via "nlp_process" from Yggdrasil
     When asgard produces sentiment values via "nlp_result" to Yggdrasil
     Then jotunheimr updates "Valhalla_Response" with those values
     And "valhalla visualizer" receives survey metrics via "survey_metrics"
