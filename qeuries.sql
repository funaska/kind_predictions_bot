
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
