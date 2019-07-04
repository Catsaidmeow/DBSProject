1) SELECT age(max(time), min(time)) as age, "UID"
FROM "Tweets"
GROUP BY "UID"
ORDER BY age DESC
LIMIT 1;

2) SELECT * FROM "Users"
WHERE "UID" = (SELECT "UID" FROM
    (SELECT "UID", count(*) as dates
     FROM
         (SELECT count(*) as amount, a."UID", a."TID"
          FROM "Retweets" a, "Retweets" b
          WHERE a."UID" =  b."TID"
            AND a."TID" = b."UID"
            AND not a."UID" = a."TID"
          GROUP BY a."UID", a."TID") as sub_query

     WHERE amount = 1
     GROUP BY "UID"
     ORDER BY dates DESC
     LIMIT 1) as sub_query2);

3) SELECT * FROM "Users"
WHERE "UID" = (SELECT "UID"
               FROM "Tweets"
               GROUP BY "UID"
               ORDER BY count(*) DESC
               LIMIT 1);

4) SELECT count(*) FROM
    (SELECT "UID", count(*) as amount
     FROM
         (SELECT count(*) as amount, a."UID", a."TID"
          FROM "Retweets" a, "Retweets" b
          WHERE a."UID" =  b."TID"
            AND a."TID" = b."UID"
            AND not a."UID" = a."TID"
          GROUP BY a."UID", a."TID") sub_query
     WHERE sub_query.amount > 1
     GROUP BY "UID") b
   WHERE amount > 1;

5) SELECT * FROM "Users"
   where "UID"=(
       select "FID" from "IsFanOf"
       group by "FID"
       order by count(*) desc
       limit 1
   );

6) SELECT count(*) FROM "Users" U
   WHERE U."UID" NOT IN (SELECT "FID" FROM "IsFanOf")
     AND U."UID" NOT IN (SELECT a."UID"
                         FROM "Retweets" a, "Retweets" b
                         WHERE a."UID" =  b."TID"
                           AND a."TID" = b."UID"
                           AND not a."UID" = a."TID"
                         GROUP BY a."UID", a."TID");