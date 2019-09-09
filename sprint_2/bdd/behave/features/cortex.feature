Feature: Evalhalla
  Thank you for taking part in this survey. The results of this survey
  will be used to demonstrate how Evalhalla can be used
  to quickly collect valuable data and provide instant access to survey results
  through a real-time dashboard for immediate consumption.
  Please take a few minutes to answer the following questions.

  Scenario: Check neo4j
     Given Neo4j is installed with APOC version "3.5.0.4"

  # Scenario: Sending and receiving survey in evalese format
  #    Given EValhalla Designer creates "TEST_SUR_evalese" in "sur_evalese" format
  #     When EValhalla Designer calls "survey" service to "store" it
  #     Then EValhalla Player calls "survey" service to "retrieve" it
  #
  # Scenario: Sending and receiving survey in template format
  #    Given EValhalla Designer creates "TEST_SUR_template" in "template" format
  #     When EValhalla Designer calls "survey" service to "store" it
  #     Then EValhalla Player calls "survey" service to "retrieve" it
  #     And Neo4j receives it and creates a "CSPS_Survey" with a number of "CSPS_Question"
  #
  # Scenario: Sending and receiving a number of survey responses
  #    Given EValhalla Player got items from "0" to "1000" of "TEST_SUR_responses"
  #     When EValhalla Player calls "response" service to "store" each of them
  #     Then Neo4j receives them and creates a number of "CSPS_Response" with "CSPS_Respondent" and "CSPS_Answer"

  Scenario: Extract free text answers and producing sentiment values
    Given EValhalla Player got items from "0" to "1" of "TEST_SUR_responses"
     When Survista calls "free_text" service to "extract" each of them
     Then it calls "free_text" servcice to "update" each of them

  # Scenario: Sending and receiving survey in evalese format
  #    Given EValhalla Designer creates "ELDP_evalese" in "sur_evalese" format
  #     When EValhalla Designer calls "survey" service to "store" it
  #     Then EValhalla Player calls "survey" service to "retrieve" it
  #
  # Scenario: Sending and receiving survey in template format
  #    Given EValhalla Designer creates "ELDP_template" in "template" format
  #     When EValhalla Designer calls "survey" service to "store" it
  #     Then EValhalla Player calls "survey" service to "retrieve" it
  #     And Neo4j receives it and creates a "CSPS_Survey" with a number of "CSPS_Question"
  #
  # Scenario: Sending and receiving a number of survey responses
  #    Given EValhalla Player got items from "0" to "1000" of "ELDP_responses"
  #     When EValhalla Player calls "response" service to "store" each of them
  #     Then Neo4j receives them and creates a number of "CSPS_Response" with "CSPS_Respondent" and "CSPS_Answer"

  # Scenario: Receiving free text answers and producing sentiment values
  #   Given "asgard" receives free text answers via "nlp_process" from Yggdrasil
  #    When asgard produces sentiment values via "nlp_result" to Yggdrasil
  #    Then jotunheimr updates "Valhalla_Response" with those values
  #    And "valhalla visualizer" receives survey metrics via "survey_metrics"
