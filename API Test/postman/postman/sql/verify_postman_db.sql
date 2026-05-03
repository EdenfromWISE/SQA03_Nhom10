-- Snapshot checks for Postman API runs (SQLite syntax)
SELECT 'qa_users_total' AS metric, COUNT(*) AS value
FROM auth_user
WHERE email LIKE 'qa_%';

SELECT 'registered_test_users' AS metric, COUNT(*) AS value
FROM auth_user
WHERE email LIKE 'qa_reg_%';

SELECT 'seed_learning_sessions' AS metric, COUNT(*) AS value
FROM learning_learningsession ls
JOIN auth_user u ON u.id = ls.user_id
WHERE u.email = 'qa_postman@example.com';

SELECT 'seed_learning_answers' AS metric, COUNT(*) AS value
FROM learning_useranswer ua
JOIN learning_learningsession ls ON ls.id = ua.session_id
JOIN auth_user u ON u.id = ls.user_id
WHERE u.email = 'qa_postman@example.com';

SELECT 'seed_chat_messages' AS metric, COUNT(*) AS value
FROM chatbot_chatmessage c
JOIN auth_user u ON u.id = c.user_id
WHERE u.email = 'qa_postman@example.com';

SELECT 'seed_mastery_rows' AS metric, COUNT(*) AS value
FROM progress_uservocabularymastery p
JOIN auth_user u ON u.id = p.user_id
WHERE u.email = 'qa_postman@example.com';
