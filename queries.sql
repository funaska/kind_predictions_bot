
SELECT *
FROM users
WHERE 1=1
LIMIT 10;


SELECT
    count(*)
FROM predictions
WHERE 1=1
LIMIT 10;


INSERT INTO users (user_id, user_name)
VALUES (1, 'admin')
;

-- DROP TABLE users;
-- DROP TABLE predictions;

-- DELETE FROM users;
-- DELETE FROM predictions;

SELECT name FROM sqlite_master WHERE type='table' AND name= 'users';
SELECT name FROM sqlite_master WHERE type='table' AND name= 'predictions';

select *
from predictions
WHERE 1=1
-- AND prediction_text like '%ещй%'
and prediction_id = 52
limit 10;

-- UPDATE predictions
-- SET prediction_text = 'Пока все смеются и угарают, вкинешь свою шутку. Все засмеются ещё громче!'
-- WHERE prediction_id = 52
-- ;
