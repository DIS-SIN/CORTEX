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
