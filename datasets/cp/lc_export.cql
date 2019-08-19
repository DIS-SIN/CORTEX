CALL apoc.export.csv.query("MATCH (p:CP_Province)-[]-(c:CP_CSD)-[]-(t:CP_CSDType) RETURN DISTINCT(c.name) AS place, p.abbr AS province, t.code AS type ORDER BY province, place, type", "/all_municipalities.tsv", {delim: '\t'});

CALL apoc.export.csv.query("MATCH (p:CP_Province)-[]-(c:CP_CSD)-[]-(t:CP_CSDType) WHERE t.code IN ['C', 'CV', 'CY', 'T'] RETURN DISTINCT(c.name) AS place, p.abbr AS province, t.code AS type ORDER BY province, place, type", "/cities_towns.tsv", {delim: '\t'});
