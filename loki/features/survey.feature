Feature: Survey design and distribution
  In order to keep Asgard an enjoyable place
  As the top boss, Odin wants to know opinion of its residents
  about the current trash collecting system
  So that he can plan upcoming budget for it

  Scenario: Odin uses Valhalla Designer to design and send survey to other gods
     Given the Trash collecting system with name "survey" and id "s1" is created in Valhalla Designer
      When its "evalese" is sent to "survey_evalese" of Yggdrasil
      And its "json" is sent to "survey_json" of Yggdrasil
      Then Valhalla Player should receive via "survey_evalese" an evalese with md5 "28ffb115129fb59c70fad33da2cabb73"
      And Jotunheimr should receive via "survey_json" a json with md5 "2bfcdcf85724896439631d7c9237c020"
