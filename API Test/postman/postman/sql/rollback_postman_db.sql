-- Roll back Postman-created data in SQLite.
-- Use on dedicated postman_test.sqlite3 only.

DELETE FROM chatbot_chatmessage
WHERE user_id IN (
    SELECT id FROM auth_user WHERE email = 'qa_postman@example.com'
);

DELETE FROM learning_useranswer
WHERE session_id IN (
    SELECT id FROM learning_learningsession
    WHERE user_id IN (SELECT id FROM auth_user WHERE email = 'qa_postman@example.com')
);

DELETE FROM learning_question
WHERE session_id IN (
    SELECT id FROM learning_learningsession
    WHERE user_id IN (SELECT id FROM auth_user WHERE email = 'qa_postman@example.com')
);

DELETE FROM learning_learningsession
WHERE user_id IN (
    SELECT id FROM auth_user WHERE email = 'qa_postman@example.com'
);

DELETE FROM progress_dailyactivity
WHERE user_id IN (
    SELECT id FROM auth_user WHERE email = 'qa_postman@example.com'
);

DELETE FROM progress_userstreak
WHERE user_id IN (
    SELECT id FROM auth_user WHERE email = 'qa_postman@example.com'
);

DELETE FROM progress_usertopicprogress
WHERE user_id IN (
    SELECT id FROM auth_user WHERE email = 'qa_postman@example.com'
);

DELETE FROM progress_uservocabularymastery
WHERE user_id IN (
    SELECT id FROM auth_user WHERE email = 'qa_postman@example.com'
);

DELETE FROM auth_user
WHERE email LIKE 'qa_reg_%';
