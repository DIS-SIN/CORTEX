CALL apoc.schema.assert(
  {
    Valhalla_Survey:['title','description','valid','version'],
    Valhalla_Question:['type', 'question', 'classified_as'],
    Valhalla_Response:['survey_uid','created'],
    GC_Language:['name']
  }, {
    Valhalla_Survey:['uid'],
    Valhalla_Question:['uid'],
    Valhalla_Response:['uid'],
    Valhalla_Respondent:['uid'],
    Valhalla_Answer:['text'],
    GC_Language:['uid']
  },
  false
);
