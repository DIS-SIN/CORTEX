Feature: Survey design and distribution
  In order to keep Asgard an enjoyable place
  As the top boss, Odin wants to know opinion of its residents
  about the current trash collecting system
  So that he can plan upcoming budget for it

  Scenario: Odin uses Valhalla Designer to design and send survey to other gods
     Given the Trash collecting system with name "evalhalla_survey" is created in Valhalla Designer
      When its "evalesemsg" is sent to "survey_evalese" of Yggdrasil
      And its "template" is sent to "survey_json" of Yggdrasil
      Then Valhalla Player should receive via "survey_evalese" an evalese with md5 "b05e58bffcad5e102a57628b181361a1"
      And a json with md5 "e904b7980100ea401184b3464f38701f" is delivered via "survey_json"
      And Jotunheimr should receive "test_sur" survey with "q_1,q_2,q_3,q_4,q_5,q_6,q_7,q_8,q_9,q_10,q_11" questions

  Scenario: Thor fills a survey using Valhalla Player
     Given Thor creates a "response" to "evalhalla_survey" survey
      When he sent this response via "survey_response" to Jotunheimr
      Then Jotunheimr extracts "11" answers
      And updates aggreagated metrics to contains response "created" from "2019-08-21T23:03:02.180Z"
      And sends free text answers via "nlp_process" to Asgard

  Scenario: Asgard process free text answers
     Given Asgard receives a free text answer "This is what" via "nlp_process"
      When it sends "0.1" as its sentiment value via "nlp_result" o Jotuheimr
      Then Jotunheimr persists this sentiment "0.1" value for "q_9"

  Scenario: Valhalla Visualizer display info
     Given the Visualizer queries responses for "test_sur"
      When metrics arrive via "survey_metrics"
      And sentiment value "0.1" also come via "nlp_result"
