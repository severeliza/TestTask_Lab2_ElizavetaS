OPTIMIZE TABLE raw_table DEDUPLICATE;
OPTIMIZE TABLE raw_table FINAL;

CREATE TABLE people
(
  `craft` String,
  `name`  String,
  `_inserted_at` DateTime
)
ENGINE = MergeTree
ORDER BY (_inserted_at); 

CREATE MATERIALIZED VIEW mv_parse_people
TO people
AS
SELECT
    JSON_VALUE(person, '$.craft') AS craft,
    JSON_VALUE(person, '$.name')  AS name,
    _inserted_at
FROM raw_table
ARRAY JOIN JSONExtractArrayRaw(raw_json, 'people') AS person;

select * from mv_parse_people;