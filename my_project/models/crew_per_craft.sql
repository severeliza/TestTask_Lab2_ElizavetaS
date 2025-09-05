SELECT
    craft,
    count(*) AS crew_size
FROM people
GROUP BY craft
ORDER BY crew_size DESC