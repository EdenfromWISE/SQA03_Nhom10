# Kế hoạch triển khai Unit Test Catalog (Backend)

## 1.1 Tools and Libraries

| Công cụ / thư viện | Loại | Trạng thái trong codebase | Mục đích |
|---|---|---|---|
| `django.test.TestCase` | Testing framework | **Đang dùng** (test stubs hiện tại) | Nền tảng unit test theo hệ `unittest` của Django. |
| `unittest.mock` (`patch`, `Mock`, `MagicMock`) | Mocking | **Đề xuất dùng** cho unit test mới | Cô lập API ngoài, AI model, email, token verify, DB side-effect không cần thiết. |
| `rest_framework.test` (`APIClient`/`APITestCase`) | API testing helper | **Có sẵn** qua DRF dependency | Kiểm thử view/API response code, payload, auth behavior. |
| `pytest` | Testing framework | **Không thấy cấu hình** | Không nằm trong phạm vi chuẩn hiện tại. |
| `Jest` / `JUnit` / `Mockito` | JS/Java testing | **Không áp dụng** cho backend Python này | Ngoài stack công nghệ hiện tại. |

---

## 1.2 Scope of Testing

### A. Các hàm/lớp/tệp **ĐƯỢC** kiểm thử

| App | Tệp | Hàm/Lớp ưu tiên test | Lý do |
|---|---|---|---|
| `students` | `students\views.py` | `GoogleIdTokenLoginView`, `PasswordResetRequestView`, `PasswordResetConfirmView` | Luồng auth quan trọng, nhiều nhánh lỗi, ảnh hưởng bảo mật/tài khoản. |
| `admin_api` | `admin_api\views.py` | `AdminUserViewSet`, `AdminVocabularyViewSet`, `AdminStatsView`, `AdminLogoutView`, `AdminPagination` | Nghiệp vụ CRUD/filter/import-export admin và response contract rõ ràng. |
| `learning` | `learning\services\question_service.py` | `generate_session_questions`, `evaluate_answer` | Core logic sinh/chấm câu hỏi. |
| `learning` | `learning\services\question_types\*.py` | `build_question`, `evaluate_answer` của `Reading/Writing/Listening/Matching/Speaking` | Thuần logic, dễ unit test, ảnh hưởng trực tiếp chất lượng bài học. |
| `learning` | `learning\services\sessions_service.py` | `create_practice_session`, `create_review_session`, `create_exam_session`, `submit_answer`, `complete_session`, `cancel_session` | Luồng session chính (practice/review/exam), cập nhật tiến độ và điểm số. |
| `progress` | `progress\services\streak_service.py` | `update_streak`, `get_streak_calendar` | Business rule streak theo ngày. |
| `progress` | `progress\services\srs_service.py` | `is_vocabulary_eligible_for_srs`, `update_review`, `get_vocabularies_due_for_review`, `get_new_vocabularies` | Logic SRS (SM-2) trọng tâm sản phẩm. |
| `progress` | `progress\views.py` | `UpcomingReviewAPIView`, `OverviewAPIView`, `DailyProgressAPIView`, `RecentSessionsAPIView` | Tổng hợp số liệu/nhóm dữ liệu dễ sai logic nếu không test. |
| `vocabulary` | `vocabulary\serializers.py`, `vocabulary\views.py`, `vocabulary\models.py` | `CourseSerializer`, `TopicDetailSerializer`, auth behavior của views, `__str__` models | Contract dữ liệu trả về cho frontend và model behavior cơ bản. |
| `chatbot` | `chatbot\actions.py` | `translate_text_to_vietnamese`, `handle_tra_tu`, `handle_lam_quiz`, `handle_phat_am_tu_vung` | Nhiều nhánh phụ thuộc API ngoài + xử lý hội thoại chính. |
| `chatbot` | `chatbot\views.py` | `ChatbotHistoryView`, `ChatbotApiEndpoint.post` | Lưu/lấy lịch sử và điều phối intent/action. |

### B. Các hàm/lớp/tệp **KHÔNG** unit test trực tiếp

| Tệp/Nhóm | Không test unit trực tiếp vì | Hướng xử lý thay thế |
|---|---|---|
| `*\migrations\*.py` | File sinh tự động, không chứa business logic cần unit test tay. | Dựa vào migration workflow + integration test DB. |
| `*\urls.py` | Mapping route tĩnh, giá trị unit thấp. | Có thể kiểm tra gián tiếp qua API tests. |
| `*\admin.py` | Cấu hình Django admin, không phải luồng nghiệp vụ chính người dùng. | Kiểm tra thủ công admin UI khi cần. |
| `*\apps.py` (đa số app) | Chỉ khai báo config; unit test không mang nhiều giá trị. | Smoke test app startup. |
| `learning\services\pronunciation_ai.py` | Phụ thuộc nặng (`torch`, `transformers`, `librosa`, `ffmpeg`), runtime tốn tài nguyên. | Mock assessor ở lớp gọi (`speaking`, `assess_pronunciation`) + integration test riêng môi trường AI. |
| `chatbot\nlu.py`, `chatbot\train_intent_model.py` | Phụ thuộc model artifacts (`joblib`, spaCy model), thiên về ML pipeline. | Test contract ở `ChatbotApiEndpoint` bằng mock `nlu_processor.parse`. |
| `core\settings.py`, `core\asgi.py`, `core\wsgi.py`, `manage.py` | Tệp cấu hình/entrypoint, không phải business function. | Smoke/deploy checks. |
| `vocabulary\management\commands\*.py` | Command nhập liệu thiên ETL, phụ thuộc file CSV môi trường. | Integration test command theo dataset mẫu riêng khi cần. |
| File dữ liệu `*.csv` trong `data\` | Dữ liệu đầu vào, không phải code logic. | Data validation/ETL checks. |

---

## 1.3 Catalog Unit Test Cases

> Tổ chức theo **Tên tệp / Tên lớp (hoặc hàm)**.  
> Mỗi test case gồm: **Test Case ID / Test Objective / Input / Expected Output / Notes**.

### `students\views.py` — `GoogleIdTokenLoginView`, `PasswordResetRequestView`, `PasswordResetConfirmView`

| Test Case ID | Test Objective | Input | Expected Output | Notes |
|---|---|---|---|---|
| UT-STU-GL-001 | Trả lỗi khi thiếu `id_token` | POST body `{}` | HTTP 400, message yêu cầu `ID token` | Không cần mock Google API. |
| UT-STU-GL-002 | Trả lỗi khi thiếu `GOOGLE_CLIENT_ID` cấu hình | POST có `id_token`, settings client_id rỗng | HTTP 500, error cấu hình OAuth | Mock settings. |
| UT-STU-GL-003 | Đăng nhập Google thành công và tạo user mới | `id_token` hợp lệ trả về email mới | HTTP 200 có `access`, `refresh`; user được tạo | Mock `id_token.verify_oauth2_token`. |
| UT-STU-GL-004 | Token hợp lệ nhưng không có email | verify trả payload không có `email` | HTTP 400 | Mock verify return dict thiếu key email. |
| UT-STU-GL-005 | Clock skew error trả thông điệp chuyên biệt | verify raise `ValueError` chứa `clock/too early` | HTTP 400, message clock sync | Kiểm tra branch xử lý regex time diff. |
| UT-STU-GL-006 | Invalid token trả 400 | verify raise `ValueError` thông thường | HTTP 400, error `Invalid token` | Mock exception. |
| UT-STU-PR-001 | Password reset request thiếu email | POST `{}` | HTTP 400 | — |
| UT-STU-PR-002 | Password reset request với email không tồn tại | POST email không có user | HTTP 200 message generic, không lộ thông tin tồn tại user | Anti-enumeration behavior. |
| UT-STU-PR-003 | Password reset request thành công trả `uid/token/reset_url` | POST email tồn tại | HTTP 200 và có `uid`, `token`, `reset_url` | Mock `send_mail` để tránh gửi thật. |
| UT-STU-PC-001 | Password reset confirm thiếu trường bắt buộc | thiếu một trong `uid/token/new_password` | HTTP 400 | — |
| UT-STU-PC-002 | Password reset confirm với `uid` không hợp lệ | `uid` decode lỗi | HTTP 400 `Invalid uid` | — |
| UT-STU-PC-003 | Password reset confirm token không hợp lệ | token sai | HTTP 400 `Invalid or expired token` | Mock token generator check false. |
| UT-STU-PC-004 | Password reset confirm thành công đổi mật khẩu | uid/token hợp lệ + password mới | HTTP 200 message thành công; password đã đổi | Verify user password hash thay đổi. |

### `admin_api\views.py` — `AdminUserViewSet`, `AdminVocabularyViewSet`, `AdminStatsView`, `AdminLogoutView`, `AdminPagination`

| Test Case ID | Test Objective | Input | Expected Output | Notes |
|---|---|---|---|---|
| UT-ADM-USR-001 | `get_queryset` filter theo `search` | Query `?search=abc` | Chỉ trả user `username` chứa `abc` | Dùng APIClient auth admin. |
| UT-ADM-USR-002 | `bulk_delete` thiếu `ids` | POST `{}` | HTTP 400 | — |
| UT-ADM-USR-003 | `bulk_delete` xóa thành công nhiều user | POST `{"ids":[id1,id2]}` | HTTP 200, users bị xóa | Tạo fixture users trước test. |
| UT-ADM-VOC-001 | Export CSV trả đúng content type/header | GET `vocabulary/export?format=csv` | HTTP 200, `text/csv`, có header cột | Kiểm tra dòng đầu CSV. |
| UT-ADM-VOC-002 | Export format không hỗ trợ | GET `?format=xlsx` | HTTP 400 | — |
| UT-ADM-VOC-003 | Import vocabulary thiếu file | POST không có `file` | HTTP 400 | — |
| UT-ADM-VOC-004 | Import vocabulary file không phải CSV | Upload `.txt` | HTTP 400 | — |
| UT-ADM-VOC-005 | Import vocabulary CSV hợp lệ | Upload CSV có dòng hợp lệ | HTTP 200, message count đúng | Có thể kèm dòng lỗi để kiểm tra skip logic. |
| UT-ADM-STA-001 | Thống kê admin trả đủ 4 chỉ số | GET `/stats` | HTTP 200 và keys: users/courses/topics/vocabulary | — |
| UT-ADM-LOGOUT-001 | Logout với refresh token lỗi vẫn trả thành công mềm | POST refresh token lỗi | HTTP 200 message fallback | Theo thiết kế hiện tại không fail cứng. |
| UT-ADM-PAG-001 | Pagination response đúng shape | gọi `get_paginated_response` với page có data | JSON có `data`, `total`, `page`, `totalPages` | Unit trực tiếp class pagination. |

### `learning\services\question_types\*.py` + `learning\services\question_service.py`

| Test Case ID | Test Objective | Input | Expected Output | Notes |
|---|---|---|---|---|
| UT-LRN-QT-READ-001 | `ReadingQuestionType.build_question` tạo cấu trúc hợp lệ | 1 vocab + pool | Có `id/type/title/prompt/answer` và `answer` là index hợp lệ | Kiểm tra `validate_question_data`. |
| UT-LRN-QT-READ-002 | `ReadingQuestionType.evaluate_answer` đúng/sai | user_answer đúng và sai | Trả `is_correct` + `score` tương ứng | — |
| UT-LRN-QT-WR-001 | `WritingQuestionType.build_question` tạo canonical/alternatives | vocabulary word mẫu | `answer.canonical` chuẩn hóa lowercase/strip | — |
| UT-LRN-QT-WR-002 | `WritingQuestionType.evaluate_answer` chấp nhận biến thể hợp lệ | user_answer thuộc alternatives | `is_correct=True` | Bao gồm case khác hoa/thường. |
| UT-LRN-QT-MAT-001 | `MatchingQuestionType.evaluate_answer` chấm điểm từng cặp | mapping đúng một phần | `score` theo tỉ lệ đúng | — |
| UT-LRN-QT-LIS-001 | `ListeningQuestionType.build_question` vẫn chạy với pool ít | pool ngắn hơn options | Question tạo được, không crash | — |
| UT-LRN-QT-SPK-001 | `SpeakingQuestionType.evaluate_answer` khi assessor chưa sẵn sàng | assessor = None | `is_correct=False`, feedback hệ thống chưa sẵn sàng | Mock app config. |
| UT-LRN-QS-001 | `QuestionService.generate_session_questions` reject vocab rỗng | `vocabularies=[]` | Raise `ValueError` | — |
| UT-LRN-QS-002 | `QuestionService.generate_session_questions` reject enabled type không hợp lệ | enabled_types chứa type lạ | Raise `ValueError` | — |
| UT-LRN-QS-003 | `QuestionService.evaluate_answer` reject question thiếu `type` | question dict không có `type` | Raise `ValueError` | — |
| UT-LRN-QS-004 | `QuestionService.get_available_question_types` trả map display names | registry mặc định | Có các type `listening/reading/writing/matching/speaking` | — |

### `learning\services\sessions_service.py` — `SessionsService`

| Test Case ID | Test Objective | Input | Expected Output | Notes |
|---|---|---|---|---|
| UT-LRN-SS-001 | `create_practice_session` lỗi khi topic không có từ | topic vocab rỗng | Raise `ValueError` | — |
| UT-LRN-SS-002 | `create_review_session` lỗi khi không có từ due | SM2 due list rỗng | Raise `ValueError` | Mock `SM2Service.get_vocabularies_due_for_review`. |
| UT-LRN-SS-003 | `create_review_session` giới hạn tối đa 20 câu | truyền total_questions > 20 | Session `total_questions <= 20` | — |
| UT-LRN-SS-004 | `create_exam_session` chặn vượt số lần thi/ngày | đã đủ `max_daily_exams_per_topic` | Raise `ValueError` | Chuẩn bị dữ liệu sessions trong ngày. |
| UT-LRN-SS-005 | `submit_answer` reject session đã hoàn thành | session có `completed_at` | Raise `ValueError` | — |
| UT-LRN-SS-006 | `submit_answer` reject question không thuộc session | `question_id` không tồn tại trong session | Raise `ValueError` | — |
| UT-LRN-SS-007 | `submit_answer` lưu answer đúng field theo kiểu dữ liệu | answer kiểu `dict`/`str`/`int` | `answer_text` hoặc `selected_option` được set đúng | Verify `UserAnswer` saved fields. |
| UT-LRN-SS-008 | `complete_session` tính điểm và cập nhật trạng thái | session có N câu, M đúng | score đúng %, set `completed_at`, `is_passed` đúng ngưỡng | — |
| UT-LRN-SS-009 | `cancel_session` không cho hủy session hoàn thành | session đã hoàn thành | Raise `ValueError` | — |
| UT-LRN-SS-010 | `complete_session` mode exam cập nhật `UserTopicProgress` | session exam pass/fail | attempts/best_score/is_passed cập nhật đúng | Kiểm tra cả nhánh tạo mới và cập nhật. |

### `progress\services\streak_service.py`, `progress\services\srs_service.py`, `progress\views.py`

| Test Case ID | Test Objective | Input | Expected Output | Notes |
|---|---|---|---|---|
| UT-PRG-STK-001 | `update_streak` lần hoạt động đầu tiên tạo streak=1 | user chưa có streak + call update | current=1, longest=1, last_active=today | — |
| UT-PRG-STK-002 | `update_streak` cùng ngày không tăng thêm | streak đã active hôm nay | current giữ nguyên | — |
| UT-PRG-STK-003 | `update_streak` ngày liên tiếp tăng streak | last_active = hôm qua | current +1, longest cập nhật | — |
| UT-PRG-STK-004 | `update_streak` đứt chuỗi thì reset current | last_active < hôm qua | current=1, longest giữ max cũ | — |
| UT-PRG-STK-005 | `get_streak_calendar` trả đầy đủ ngày trong tháng | year/month cụ thể | số phần tử `days` đúng số ngày tháng | — |
| UT-PRG-SM2-001 | `is_vocabulary_eligible_for_srs` true khi chưa có mastery | user+vocab mới | `True` | — |
| UT-PRG-SM2-002 | `update_review` trả `None` khi chưa đến hạn và không force | mastery next_review_date > now | `None` | — |
| UT-PRG-SM2-003 | `update_review` với trả lời đúng tăng repetitions/interval | is_correct=True | mastery cập nhật đúng quy tắc | Kiểm tra clamp EF >=1.3. |
| UT-PRG-SM2-004 | `update_review` với trả lời sai reset repetitions/interval | is_correct=False | repetitions=0, interval=1 | — |
| UT-PRG-SM2-005 | `get_vocabularies_due_for_review` lọc đúng due list | nhiều mastery với due/not-due | chỉ trả mastery `<= now`, đúng order | — |
| UT-PRG-VIEW-001 | `UpcomingReviewAPIView` nhóm từ quá hạn vào ngày hôm nay | có overdue + future mastery | response list có today count gồm overdue | API test với user auth. |
| UT-PRG-VIEW-002 | `OverviewAPIView` trả đủ 4 chỉ số tổng quan | dữ liệu mastery có trong ngày | response keys đúng, giá trị đúng theo dữ liệu mẫu | — |
| UT-PRG-VIEW-003 | `DailyProgressAPIView` luôn trả 7 mục T2..CN | dữ liệu thực hành trong tuần | list length=7, labels đúng | — |
| UT-PRG-VIEW-004 | `RecentSessionsAPIView` format phiên gần đây đúng contract | có session practice/review/exam completed | mỗi item có `time/type/wordsCount/result/status/learnedAt` | — |

### `vocabulary\models.py`, `vocabulary\serializers.py`, `vocabulary\views.py`

| Test Case ID | Test Objective | Input | Expected Output | Notes |
|---|---|---|---|---|
| UT-VOC-MOD-001 | `__str__` của `Course/Topic/Vocabulary` đúng format | tạo model mẫu | Chuỗi trả về đúng theo thiết kế hiện tại | Test đơn giản nhưng giúp bắt regression rename. |
| UT-VOC-SER-001 | `CourseSerializer` trả nested `topics` | course có topics | JSON có danh sách `topics` đúng fields | — |
| UT-VOC-SER-002 | `TopicDetailSerializer` trả nested `vocabularies` | topic có vocabularies | JSON có `vocabularies` đúng field contract | — |
| UT-VOC-VIEW-001 | `CourseListView` yêu cầu authentication | GET anonymous | HTTP 401/403 theo auth config | — |
| UT-VOC-VIEW-002 | `CourseDetailView` trả đúng dữ liệu course | GET auth + pk hợp lệ | HTTP 200, payload course đúng | — |
| UT-VOC-VIEW-003 | `TopicDetailView` trả đúng dữ liệu topic detail | GET auth + topic pk | HTTP 200 và có vocabulary list | — |

### `chatbot\actions.py`, `chatbot\views.py` — `ChatbotHistoryView`, `ChatbotApiEndpoint`

| Test Case ID | Test Objective | Input | Expected Output | Notes |
|---|---|---|---|---|
| UT-CHB-ACT-001 | `translate_text_to_vietnamese` trả `"Không có"` khi input rỗng | `text_to_translate=""` | Chuỗi `"Không có"` | — |
| UT-CHB-ACT-002 | `translate_text_to_vietnamese` fallback khi API lỗi | requests raise exception | Trả lại text gốc | Mock `requests.get`. |
| UT-CHB-ACT-003 | `handle_tra_tu` khi thiếu entity từ vựng | entities không có `tu_vung` | Trả message hỏi lại từ cần tra | — |
| UT-CHB-ACT-004 | `handle_lam_quiz` khi vocab < 4 | DB có <4 vocabulary | Trả dict type `text`, message cảnh báo | — |
| UT-CHB-ACT-005 | `handle_lam_quiz` khi đủ dữ liệu | DB có >=4 vocabulary | Trả dict type `quiz_offer`, số câu <=10 | — |
| UT-CHB-ACT-006 | `handle_phat_am_tu_vung` thiếu từ | entities không có `tu_vung` | Trả message hỏi từ cần phát âm | — |
| UT-CHB-HIS-001 | `ChatbotHistoryView.get` chỉ trả lịch sử user hiện tại, đúng thứ tự | 2 user có chat messages | Response chỉ chứa messages của user request, ordered by timestamp | APIClient auth. |
| UT-CHB-HIS-002 | `ChatbotHistoryView.delete` xóa lịch sử user hiện tại | user có messages | HTTP 200, messages user đó = 0 | Không ảnh hưởng user khác. |
| UT-CHB-API-001 | `ChatbotApiEndpoint.post` reject message rỗng | POST `{"message":"   "}` | HTTP 400 | — |
| UT-CHB-API-002 | `ChatbotApiEndpoint.post` dùng `last_vocab_word` khi intent cần từ nhưng thiếu entity | session có `last_vocab_word`, intent `tra_tu`/`phat_am_tu_vung` | Response từ action tương ứng, không hỏi lại | Mock `nlu_processor.parse` + action handlers. |
| UT-CHB-API-003 | `ChatbotApiEndpoint.post` lưu cả user message và assistant message | gửi message hợp lệ | DB tạo 2 `ChatMessage` đúng role/content | — |
| UT-CHB-API-004 | `ChatbotApiEndpoint.post` cắt lịch sử vượt 1000 message | user có >1000 messages trước request | Sau request tổng messages user <=1000 | Kiểm tra logic trim timestamp. |

---

## Ghi chú triển khai test

| Chủ đề | Quy ước |
|---|---|
| Tổ chức file test | `app/tests.py` hiện có thể tách thành `app/tests/test_<module>.py` khi triển khai thực tế. |
| Mock bắt buộc | Google token verify, gọi HTTP ngoài (`requests`), email, NLU parse, AI assessor, model loading. |
| Dữ liệu test | Dùng factory/fixture nhỏ, tránh phụ thuộc CSV lớn. |
| Tiêu chí ưu tiên | Ưu tiên test business logic có nhánh lỗi và contract API trả cho frontend. |
