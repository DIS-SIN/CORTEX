>>>SURVEY_JSON
WITH event, apoc.convert.fromJsonMap(event.content) AS c
  // Make (or update) the Survey, setting the ID and format
  MERGE (s:Valhalla_Survey {uid: event.uid, format: event.format})
WITH s, c
  // Set the survey title, description (w/both languages) version number and valid date range
  SET s.title = [c['title']['en'], c['title']['fr']], s.description = [c['description']['en'], c['description']['fr']], s.valid = [c['valid']['from'], c['valid']['to']], s.version = c.version

WITH s, c['questions'] AS questions
  // Transform event.content.questions to individual rows with variable name cq
  UNWIND questions AS cq

WITH s, cq

  // If event.content.question.qid is not 'none'
  FOREACH (dummy IN CASE WHEN cq['qid'] <> 'none' THEN [1] ELSE [] END |

    // Make (or update) the Question, setting the uid
    MERGE (q:Valhalla_Question {uid: cq['cortex']['uid']})

    // If questionType is SINGLE_CHOICE, set Question.SINGLE_CHOICE
    FOREACH (dummy IN CASE WHEN cq['cortex']['questionType'] = 'SINGLE_CHOICE' THEN [1] ELSE [] END | SET q:SINGLE_CHOICE)

    // If questionType is MULTI_CHOICE, set Question.MULTI_CHOICE
    FOREACH (dummy IN CASE WHEN cq['cortex']['questionType'] = 'MULTI_CHOICE' THEN [1] ELSE [] END | SET q:MULTI_CHOICE)

    // If questionType is FREE_TEXT, set Question.FREE_TEXT
    FOREACH (dummy IN CASE WHEN cq['cortex']['questionType'] = 'FREE_TEXT' THEN [1] ELSE [] END | SET q:FREE_TEXT)

    // Set this questions type, set the question text (both languages), classification, and using apoc to convert to Json set the options
    SET q.type = cq['cortex']['questionType'], q.question = [cq['question']['en'], cq['question']['fr']], q.classified_as = cq['cortex']['classifiedAs'], q.options = apoc.convert.toJson(cq['options'])

    // Make (or update) a relationship from this Question to the original Survey
    // Set the relationships prop n to event.content.questions[cortex][atOrder]
    MERGE (q)<-[:AT_ORDER {n: cq['cortex']['atOrder']}]-(s)
  )
<<<

>>>SURVEY_RESPONSE
// Alias event as event, and convert event.content to json then alias as c
WITH event, apoc.convert.fromJsonMap(event.content) AS c

  // Make (or update) the Survey, setting uid from event.response.conducted
  MERGE (s:Valhalla_Survey {uid: c['response']['conducted']})

    //Make (or update) the Response, set the uid
    MERGE (r:Valhalla_Response {uid: event.uid})

      // Make relationship from the Response to the Survey
      MERGE (r)-[:RESPOND_TO]->(s)
        SET r.survey_uid = c['response']['conducted'], r.content = event.content

//Alias the Response as r, c as c, and event.content.respondent as cr (user information)
WITH r, c, c['respondent'] AS cr

  // Make the Respondent information, creating a unique ID
  MERGE (d:Valhalla_Respondent {uid: apoc.create.uuid()})

    // If cr.fluent_as is not null/empty
    FOREACH (dummy IN CASE WHEN cr.fluent_at IS NOT NULL THEN [1] ELSE [] END |
      // Make the language and relate the Respondent (User) back to the language
      MERGE (a:GC_Language {uid: TRIM(cr.fluent_at)})
        MERGE (d)-[:FLUENT_AT]->(a))

    // If cr.located_in is not null/empty
    FOREACH (dummy IN CASE WHEN cr.located_in IS NOT NULL THEN [1] ELSE [] END |
      // Make the province information by:
      // Split the event.content.respondent.located_in based on a comma, take the second record
      MERGE (p:CP_Province {uid: SPLIT(TRIM(SPLIT(cr.located_in, ',')[1]), ' ')[0]})

        // Make the city information by:
        // Split the event.content.respondent.located_in based on a comma, take the first record
        // Trim leading/trailing spaces
      	MERGE (a:CP_CSD {name: TRIM(SPLIT(cr.located_in, ',')[0])})

          // Relate city to province information
        	MERGE (a)-[:CSD_IN_PR]->(p)

            // Relate respondent to city information
        		MERGE (d)-[:LOCATED_IN]->(a))

    // If cr.department is not null/empty
    FOREACH (dummy IN CASE WHEN cr.in_department IS NOT NULL THEN [1] ELSE [] END |
      // Make the organization information from department
      // Split based on ( and trim leading/trailing spaces

      // Relate respondent to org information
      MERGE (a:GC_Org {en_name: TRIM(SPLIT(cr.in_department, '(')[0])})
        MERGE (d)-[:IN_DEPARTMENT]->(a))

    // If cr.work_as is not null/empty
    FOREACH (dummy IN CASE WHEN cr.work_as IS NOT NULL THEN [1] ELSE [] END |
      // Make the classification from cr.work_as, trimming any leading/trailing spaces
      // Make a relationship from respondent to classification
      MERGE (a:GC_ClsLvl {uid: TRIM(cr.work_as)})
        MERGE (d)-[:WORK_AS]->(a))

    // Make a relationship from respondent to response, setting the creation information
    MERGE (d)-[:RESPONDENT_OF]->(r)
      SET r.created = [c['created']['from'], c['created']['to']]

WITH r, c, c['questions'] AS questions
  // Transform event.content.questions to individual rows with variable name cq
  UNWIND questions AS cq
WITH r, c, cq
  // Make Question, setting the uid
  MERGE (q:Valhalla_Question {uid: cq['uid']})

// If stats are null, then map is empty
// If stats are not null, then map is read from stats (converted using apoc)
WITH r, c, cq, q, CASE WHEN q.stats IS NULL THEN apoc.map.fromPairs([]) ELSE apoc.convert.fromJsonMap(q.stats) END AS map

  // If Valhalla_Question type (set from JSON_SURVEY) does not equal classified
  FOREACH (dummy IN CASE WHEN q.type <> 'CLASSIFIED' THEN [1] ELSE [] END |
    // If the current question type is SINGLE CHOICE or FREE TEXT
    FOREACH (dummy IN CASE WHEN (cq['questionType'] = 'SINGLE_CHOICE' OR cq['questionType'] = 'FREE_TEXT') THEN [1] ELSE [] END |
      // Make an Answer, setting the text
      // Relate the response to this answer
      // Relate this answer to the original question
      MERGE (a:Valhalla_Answer {text: cq['questionAnswer']})
        MERGE (r)-[:AT_ORDER {n: cq['atOrder']}]->(a)
          MERGE (a)-[:ANSWER_OF]->(q)
            // Add the new question stats to the map, then set the stats for the question
            // Increment the answer counter + 1 (or set to 1 if first time)
            SET q.stats = apoc.convert.toJson(apoc.map.setKey(map, cq['questionAnswer'], apoc.map.get(map, cq['questionAnswer'], 0) + 1)),
                q.answer_total = CASE WHEN q.answer_total IS NULL THEN 1 ELSE q.answer_total + 1 END
    )

    // If the current question type is MULTI_CHOICE
    FOREACH (dummy IN CASE WHEN cq['questionType'] = 'MULTI_CHOICE' THEN [1] ELSE [] END |
      // Loop through the answers provided
      FOREACH (answer IN cq['questionAnswer'] |
        // Make an Answer object
        MERGE (a:Valhalla_Answer {text: answer})
          MERGE (r)-[:AT_ORDER {n: cq['atOrder']}]->(a)
            MERGE (a)-[:ANSWER_OF]->(q)
              // Add the new question stats to the map, then set the stats for the question
              // Increment the answer counter + 1 (or set to 1 if first time)
              SET q.stats = apoc.convert.toJson(apoc.map.setKey(map, answer, apoc.map.get(map, answer, 0) + 1))
      )
      SET q.answer_total = CASE WHEN q.answer_total IS NULL THEN 1 ELSE q.answer_total + 1 END
    )
  )

WITH r, c, cq, q, CASE WHEN q.stats IS NULL THEN apoc.map.fromPairs([]) ELSE apoc.convert.fromJsonMap(q.stats) END AS map
  // If the Valhalla_Question (set by JSON_SURVEY) is classified as GC Org
  FOREACH (dummy IN CASE WHEN q.classified_as = 'GC_Org' THEN [1] ELSE [] END |
    // Make (or update) the GC_Org
    // set the en_name from the questionAnswer, removing the content after the first parenthesis
    MERGE (a:GC_Org {en_name: TRIM(SPLIT(cq['questionAnswer'], '(')[0])})
      MERGE (r)-[:AT_ORDER {n: cq['atOrder']}]->(a)
        MERGE (a)-[:ANSWER_OF]->(q)
          // Add the new question stats to the map, then set the stats for the question
          // Increment the answer counter + 1 (or set to 1 if first time)
          SET q.stats = apoc.convert.toJson(apoc.map.setKey(map, TRIM(SPLIT(cq['questionAnswer'], '(')[0]), apoc.map.get(map, TRIM(SPLIT(cq['questionAnswer'], '(')[0]), 0) + 1)),
              q.answer_total = CASE WHEN q.answer_total IS NULL THEN 1 ELSE q.answer_total + 1 END
  )

WITH r, c, cq, q, CASE WHEN q.stats IS NULL THEN apoc.map.fromPairs([]) ELSE apoc.convert.fromJsonMap(q.stats) END AS map
  // If the Valhalla_Question (set by JSON_SURVEY) is classified as GC_Language
  // Make (or update) the GC_Language
  // set the name from the questionAnswer, removing the leading/trailing spaces
  // Add the new question stats to the map, then set the stats for the question
  // Increment the answer counter + 1 (or set to 1 if first time)
  FOREACH (dummy IN CASE WHEN q.classified_as = 'GC_Language' THEN [1] ELSE [] END |
    MERGE (a:GC_Language {name: TRIM(cq['questionAnswer'])})
      MERGE (r)-[:AT_ORDER {n: cq['atOrder']}]->(a)
        MERGE (a)-[:ANSWER_OF]->(q)
          SET q.stats = apoc.convert.toJson(apoc.map.setKey(map, TRIM(cq['questionAnswer']), apoc.map.get(map, TRIM(cq['questionAnswer']), 0) + 1)),
              q.answer_total = CASE WHEN q.answer_total IS NULL THEN 1 ELSE q.answer_total + 1 END
  )

WITH r, c, cq, q, CASE WHEN q.stats IS NULL THEN apoc.map.fromPairs([]) ELSE apoc.convert.fromJsonMap(q.stats) END AS map
  // If the Valhalla_Question (set by JSON_SURVEY) is classified as GC_Language
  // Make (or update) the GC_Language
  // set the name from the questionAnswer, removing the leading/trailing spaces
  // Add the new question stats to the map, then set the stats for the question
  // Increment the answer counter + 1 (or set to 1 if first time)
  FOREACH (dummy IN CASE WHEN q.classified_as = 'GC_ClsLvl' THEN [1] ELSE [] END |
    MERGE (a:GC_ClsLvl {uid: TRIM(cq['questionAnswer'])})
      MERGE (r)-[:AT_ORDER {n: cq['atOrder']}]->(a)
        MERGE (a)-[:ANSWER_OF]->(q)
          SET q.stats = apoc.convert.toJson(apoc.map.setKey(map, TRIM(cq['questionAnswer']), apoc.map.get(map, TRIM(cq['questionAnswer']), 0) + 1)),
              q.answer_total = CASE WHEN q.answer_total IS NULL THEN 1 ELSE q.answer_total + 1 END
  )

WITH r, c, cq, q, CASE WHEN q.stats IS NULL THEN apoc.map.fromPairs([]) ELSE apoc.convert.fromJsonMap(q.stats) END AS map
  // If the Valhalla_Question (set by JSON_SURVEY) is classified as GC_Language
  // Make (or update) the GC_Language
  // set the name from the questionAnswer, removing the leading/trailing spaces
  // Add the new question stats to the map, then set the stats for the question
  // Increment the answer counter + 1 (or set to 1 if first time)
  FOREACH (dummy IN CASE WHEN q.classified_as = 'CP_CSD' THEN [1] ELSE [] END |
    MERGE (p:CP_Province {uid: SPLIT(TRIM(SPLIT(cq['questionAnswer'], ',')[1]), ' ')[0]})
      MERGE (a:CP_CSD {name: TRIM(SPLIT(cq['questionAnswer'], ',')[0])})
        MERGE (a)-[:CSD_IN_PR]->(p)
          MERGE (r)-[:AT_ORDER {n: cq['atOrder']}]->(a)
            MERGE (a)-[:ANSWER_OF]->(q)
              SET q.stats = apoc.convert.toJson(apoc.map.setKey(map, TRIM(SPLIT(cq['questionAnswer'], ',')[0]), apoc.map.get(map, TRIM(SPLIT(cq['questionAnswer'], ',')[0]), 0) + 1)),
                  q.answer_total = CASE WHEN q.answer_total IS NULL THEN 1 ELSE q.answer_total + 1 END
  )

WITH DISTINCT(r) AS r, c, COLLECT(DISTINCT(q)) AS qc
WITH r, c, qc, REDUCE(m=[], q IN c['questions'] | CASE WHEN q['questionType'] = 'FREE_TEXT' THEN m + [apoc.map.fromPairs([['uid', q['uid']], ['text', q['questionAnswer']]])] ELSE m END) AS data
WITH r, qc, apoc.map.fromPairs([['uid', r.uid], ['survey_uid', r.survey_uid], ['data', data]]) AS map
    CALL streams.publish('nlp_process', map)

// Alias the respondent, content, questions as collection
WITH r, REDUCE(m=[], q IN qc | m + [apoc.map.fromPairs([['uid', q.uid], ['total', q.answer_total], ['stats', q.stats], ['classifiedAs', q.classified_as], ['questionType', q.type], ['question', apoc.convert.toJson(q.question)]])]) AS data
WITH r, apoc.map.fromPairs([['uid', r.uid], ['survey_uid', r.survey_uid], ['data', data]]) AS map
    // Publish this map to kafka, using topic survey_metrics
    CALL streams.publish('survey_metrics', map)

RETURN 1
<<<
