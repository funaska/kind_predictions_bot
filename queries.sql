
SELECT *
FROM users
WHERE 1=1
LIMIT 10;


SELECT
    *
--     count(*)
-- approval_state, count(*)
FROM predictions
WHERE 1=1
-- and approval_state = 'not approved'
-- and approval_state = 'approved'
-- and prediction_text = '/suggest'
ORDER BY prediction_id desc
LIMIT 10;


-- INSERT INTO users (user_id, user_name)
-- VALUES (1, 'admin')
-- ;

-- DROP TABLE users;
-- DROP TABLE predictions;

-- DELETE FROM users;
-- DELETE FROM predictions;
-- DELETE FROM predictions where prediction_text = '/suggest';

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
-- delete
-- UPDATE predictions set prediction_text = 'Сегодня твой день пройдет офигенно! Так что выше нос и не грусти ты самый прекрасный человечек на свете!'
-- select *
-- from predictions
-- where prediction_text = 'Сегодня твой день пройдет офигенно! Так что выше нос и не грусти ты самый прекрасный человечек на свете!'
-- WHERE prediction_text like '/suggest %'
;
