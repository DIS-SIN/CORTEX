CREATE CONSTRAINT ON (n:CP_PostCode) ASSERT n.code IS UNIQUE;
CREATE CONSTRAINT ON (n:CP_Province) ASSERT n.uid IS UNIQUE;
CREATE INDEX ON :CP_Province(abbr);
CREATE INDEX ON :CP_Province(en_name);
CREATE INDEX ON :CP_Province(fr_name);
CREATE CONSTRAINT ON (n:CP_CSD) ASSERT n.uid IS UNIQUE;
CREATE INDEX ON :CP_CSD(name);
CREATE CONSTRAINT ON (n:CP_CSDType) ASSERT n.code IS UNIQUE;
CREATE INDEX ON :CP_CSDType(name);
CREATE INDEX ON :CP_Community(name);
CREATE INDEX ON :CP_Community(name, csd_uid);
CREATE INDEX ON :CP_Location(point);
CREATE CONSTRAINT ON (n:GC_Org) ASSERT n.dn IS UNIQUE;
CREATE INDEX ON :GC_Org(en_abbr);
CREATE INDEX ON :GC_Org(fr_abbr);
CREATE INDEX ON :GC_Org(en_name);
CREATE INDEX ON :GC_Org(fr_name);
CREATE INDEX ON :GC_Org(addr);
CREATE INDEX ON :GC_Org(city);
CREATE INDEX ON :GC_Org(pc);
CREATE CONSTRAINT ON (n:GC_OccGrp) ASSERT n.uid IS UNIQUE;
CREATE INDEX ON :GC_OccGrp(en_name);
CREATE INDEX ON :GC_OccGrp(fr_name);
CREATE CONSTRAINT ON (n:GC_JobCls) ASSERT n.uid IS UNIQUE;
CREATE INDEX ON :GC_JobCls(en_name);
CREATE INDEX ON :GC_JobCls(fr_name);
CREATE CONSTRAINT ON (n:GC_ClsLvl) ASSERT n.uid IS UNIQUE;
CREATE CONSTRAINT ON (n:CSPS_Survey) ASSERT n.uid IS UNIQUE;
CREATE INDEX ON :CSPS_Survey(title);
CREATE INDEX ON :CSPS_Survey(description);
CREATE INDEX ON :CSPS_Survey(valid);
CREATE INDEX ON :CSPS_Survey(version);
CREATE CONSTRAINT ON (n:CSPS_Question) ASSERT n.uid IS UNIQUE;
CREATE INDEX ON :CSPS_Question(type);
CREATE INDEX ON :CSPS_Question(question);
CREATE INDEX ON :CSPS_Question(classified_as);
CREATE CONSTRAINT ON (n:CSPS_Response) ASSERT n.uid IS UNIQUE;
CREATE INDEX ON :CSPS_Response(created);
CREATE CONSTRAINT ON (n:CSPS_Respondent) ASSERT n.uid IS UNIQUE;
CREATE CONSTRAINT ON (n:CSPS_Answer) ASSERT n.text IS UNIQUE;
CREATE CONSTRAINT ON (n:GC_Language) ASSERT n.uid IS UNIQUE;
CALL db.constraints();
CALL db.indexes();
CALL db.awaitIndexes();
