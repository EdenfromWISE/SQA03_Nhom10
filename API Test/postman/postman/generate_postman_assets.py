from __future__ import annotations

import csv
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
COLLECTION_PATH = ROOT / "E-Vocab-API.postman_collection.json"
ENV_PATH = ROOT / "E-Vocab-Local.postman_environment.json"
TESTCASE_CSV_PATH = ROOT / "api_testcases.csv"


@dataclass
class TestCase:
    case_id: str
    folder: str
    name: str
    method: str
    path: str
    auth: bool = False
    body: dict[str, Any] | None = None
    raw_body: str | None = None
    expected_status: list[int] | str = field(default_factory=lambda: [200])
    db_check: str = "N/A"
    rollback_scope: str = "N/A"
    pre_request: list[str] | None = None
    tests_extra: list[str] | None = None


def _js_lines(lines: list[str] | None) -> list[str]:
    return lines or []


def _status_assertion(expected_status: list[int] | str) -> list[str]:
    if isinstance(expected_status, str) and expected_status == "not_5xx":
        return [
            'pm.test("Status is not 5xx", function () {',
            "  pm.expect(pm.response.code).to.be.below(500);",
            "});",
        ]

    statuses = expected_status if isinstance(expected_status, list) else [200]
    return [
        'pm.test("Status code is expected", function () {',
        f"  pm.expect({statuses}).to.include(pm.response.code);",
        "});",
    ]


def _test_script(case: TestCase) -> list[str]:
    script = [
        f'pm.test("{case.case_id} is traceable", function () {{',
        f'  pm.expect(pm.info.requestName).to.include("{case.case_id}");',
        "});",
    ]
    script.extend(_status_assertion(case.expected_status))
    script.extend(
        [
            "pm.test('Response time < 5000ms', function () {",
            "  pm.expect(pm.response.responseTime).to.be.below(5000);",
            "});",
        ]
    )
    script.extend(_js_lines(case.tests_extra))
    return script


def _request_body(case: TestCase) -> dict[str, Any] | None:
    if case.raw_body is not None:
        return {
            "mode": "raw",
            "raw": case.raw_body,
            "options": {"raw": {"language": "json"}},
        }
    if case.body is not None:
        return {
            "mode": "raw",
            "raw": json.dumps(case.body, indent=2),
            "options": {"raw": {"language": "json"}},
        }
    return None


def _to_postman_item(case: TestCase) -> dict[str, Any]:
    headers: list[dict[str, str]] = []
    body = _request_body(case)
    if body is not None:
        headers.append({"key": "Content-Type", "value": "application/json"})
    if case.auth:
        headers.append({"key": "Authorization", "value": "Bearer {{access_token}}"})

    events = []
    if case.pre_request:
        events.append(
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "exec": case.pre_request,
                },
            }
        )
    events.append(
        {
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": _test_script(case),
            },
        }
    )

    request_obj: dict[str, Any] = {
        "method": case.method,
        "header": headers,
        "url": "{{base_url}}" + case.path,
    }
    if body is not None:
        request_obj["body"] = body

    return {
        "name": f"{case.case_id} | {case.name}",
        "event": events,
        "request": request_obj,
        "response": [],
    }


def _cases() -> list[TestCase]:
    return [
        TestCase(
            case_id="TC-AUTH-REG-001",
            folder="AUTH",
            name="Register new account",
            method="POST",
            path="/api/auth/registration/",
            body={
                "email": "{{registration_email}}",
                "username": "{{registration_username}}",
                "password1": "{{registration_password}}",
                "password2": "{{registration_password}}",
            },
            expected_status=[200, 201],
            db_check="auth_user row exists for registration_email",
            rollback_scope="Delete qa_reg_* users",
            pre_request=[
                "var runTs = Date.now();",
                'pm.environment.set("registration_email", "qa_reg_" + runTs + "@example.com");',
                'pm.environment.set("registration_username", "qa_reg_" + runTs);',
            ],
        ),
        TestCase(
            case_id="TC-AUTH-REG-VERIFY-001",
            folder="AUTH",
            name="Verify email with invalid key",
            method="POST",
            path="/api/auth/registration/verify-email/",
            body={"key": "invalid-key"},
            expected_status=[400, 404],
            db_check="No new auth_user row",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-AUTH-REG-RESEND-001",
            folder="AUTH",
            name="Resend verification email",
            method="POST",
            path="/api/auth/registration/resend-email/",
            body={"email": "{{registration_email}}"},
            expected_status="not_5xx",
            db_check="No destructive changes",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-AUTH-LOGIN-001",
            folder="AUTH",
            name="Login with seeded account",
            method="POST",
            path="/api/auth/login/",
            body={"email": "{{seed_email}}", "password": "{{seed_password}}"},
            expected_status=[200, 201],
            db_check="Auth token issued",
            rollback_scope="None",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                'var access = data.access || data.key || "";',
                "pm.expect(access).to.be.a('string').and.not.empty;",
                "pm.environment.set('access_token', access);",
                "if (data.refresh) { pm.environment.set('refresh_token', data.refresh); }",
            ],
        ),
        TestCase(
            case_id="TC-AUTH-USER-001",
            folder="AUTH",
            name="Get current user",
            method="GET",
            path="/api/auth/user/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-AUTH-USER-UPDATE-001",
            folder="AUTH",
            name="Update current user profile fields",
            method="PATCH",
            path="/api/auth/user/update/",
            auth=True,
            body={"first_name": "QA", "last_name": "Postman"},
            expected_status=[200],
            db_check="auth_user and/or students_userprofile updated",
            rollback_scope="Reset seeded user names in rollback",
        ),
        TestCase(
            case_id="TC-AUTH-USER-AVATAR-NEG-001",
            folder="AUTH",
            name="Avatar upload without file",
            method="POST",
            path="/api/auth/user/avatar/",
            auth=True,
            expected_status=[400],
            db_check="No avatar path change",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-AUTH-GOOGLE-MISSING-001",
            folder="AUTH",
            name="Google login missing token",
            method="POST",
            path="/api/auth/google/id-token/",
            body={},
            expected_status=[400],
            db_check="No user created",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-AUTH-PWD-RESET-REQ-001",
            folder="AUTH",
            name="Password reset request",
            method="POST",
            path="/api/auth/password/reset/",
            body={"email": "{{seed_email}}"},
            expected_status=[200],
            db_check="Token generated for seeded user",
            rollback_scope="Reset password back to seed value",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                "pm.expect(data).to.have.property('uid');",
                "pm.expect(data).to.have.property('token');",
                "pm.environment.set('reset_uid', data.uid);",
                "pm.environment.set('reset_token', data.token);",
            ],
        ),
        TestCase(
            case_id="TC-AUTH-PWD-RESET-CONFIRM-001",
            folder="AUTH",
            name="Password reset confirm",
            method="POST",
            path="/api/auth/password/reset/confirm/",
            body={
                "uid": "{{reset_uid}}",
                "token": "{{reset_token}}",
                "new_password": "{{new_password}}",
            },
            expected_status=[200],
            db_check="Password hash changed",
            rollback_scope="Password changed back later",
        ),
        TestCase(
            case_id="TC-AUTH-LOGIN-NEWPASS-001",
            folder="AUTH",
            name="Login with new password",
            method="POST",
            path="/api/auth/login/",
            body={"email": "{{seed_email}}", "password": "{{new_password}}"},
            expected_status=[200, 201],
            db_check="Auth token issued",
            rollback_scope="None",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                'var access = data.access || data.key || "";',
                "pm.expect(access).to.be.a('string').and.not.empty;",
                "pm.environment.set('access_token', access);",
                "if (data.refresh) { pm.environment.set('refresh_token', data.refresh); }",
            ],
        ),
        TestCase(
            case_id="TC-AUTH-PWD-CHANGE-001",
            folder="AUTH",
            name="Password change back to seed password",
            method="POST",
            path="/api/auth/password/change/",
            auth=True,
            body={
                "old_password": "{{new_password}}",
                "new_password1": "{{seed_password}}",
                "new_password2": "{{seed_password}}",
            },
            expected_status=[200],
            db_check="Password hash changed",
            rollback_scope="Seed password reapplied in rollback",
        ),
        TestCase(
            case_id="TC-AUTH-LOGIN-RESETBACK-001",
            folder="AUTH",
            name="Login with restored seed password",
            method="POST",
            path="/api/auth/login/",
            body={"email": "{{seed_email}}", "password": "{{seed_password}}"},
            expected_status=[200, 201],
            db_check="Auth token issued",
            rollback_scope="None",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                'var access = data.access || data.key || "";',
                "pm.expect(access).to.be.a('string').and.not.empty;",
                "pm.environment.set('access_token', access);",
                "if (data.refresh) { pm.environment.set('refresh_token', data.refresh); }",
            ],
        ),
        TestCase(
            case_id="TC-AUTH-LOGOUT-001",
            folder="AUTH",
            name="Logout current token",
            method="POST",
            path="/api/auth/logout/",
            auth=True,
            body={"refresh": "{{refresh_token}}"},
            expected_status="not_5xx",
            db_check="Session/token invalidation per backend config",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-ACC-LOGIN-PAGE-001",
            folder="ACCOUNTS",
            name="Allauth login page",
            method="GET",
            path="/accounts/login/",
            expected_status=[200, 302],
            db_check="Read-only HTML interface check",
            rollback_scope="None",
            tests_extra=[
                "var contentType = pm.response.headers.get('Content-Type') || '';",
                "pm.test('HTML content returned', function () {",
                "  pm.expect(contentType.toLowerCase()).to.include('text/html');",
                "});",
            ],
        ),
        TestCase(
            case_id="TC-ACC-SIGNUP-PAGE-001",
            folder="ACCOUNTS",
            name="Allauth signup page",
            method="GET",
            path="/accounts/signup/",
            expected_status=[200, 302],
            db_check="Read-only HTML interface check",
            rollback_scope="None",
            tests_extra=[
                "var contentType = pm.response.headers.get('Content-Type') || '';",
                "pm.test('HTML content returned', function () {",
                "  pm.expect(contentType.toLowerCase()).to.include('text/html');",
                "});",
            ],
        ),
        TestCase(
            case_id="TC-ACC-PWD-RESET-PAGE-001",
            folder="ACCOUNTS",
            name="Allauth password reset page",
            method="GET",
            path="/accounts/password/reset/",
            expected_status=[200, 302],
            db_check="Read-only HTML interface check",
            rollback_scope="None",
            tests_extra=[
                "var contentType = pm.response.headers.get('Content-Type') || '';",
                "pm.test('HTML content returned', function () {",
                "  pm.expect(contentType.toLowerCase()).to.include('text/html');",
                "});",
            ],
        ),
        TestCase(
            case_id="TC-VOC-COURSES-ANON-001",
            folder="VOCABULARY",
            name="Course list requires auth",
            method="GET",
            path="/api/vocabulary/courses/",
            expected_status=[401, 403],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-VOC-COURSES-001",
            folder="VOCABULARY",
            name="Get course list",
            method="GET",
            path="/api/vocabulary/courses/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
            tests_extra=[
                "var data = [];",
                "try { data = pm.response.json(); } catch (e) { data = []; }",
                "if (Array.isArray(data) && data.length > 0) {",
                "  pm.environment.set('course_id', data[0].id);",
                "  if (Array.isArray(data[0].topics) && data[0].topics.length > 0) {",
                "    pm.environment.set('topic_id', data[0].topics[0].id);",
                "  }",
                "}",
            ],
        ),
        TestCase(
            case_id="TC-VOC-COURSE-DETAIL-001",
            folder="VOCABULARY",
            name="Get course detail",
            method="GET",
            path="/api/vocabulary/courses/{{course_id}}/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-VOC-TOPIC-DETAIL-001",
            folder="VOCABULARY",
            name="Get topic detail",
            method="GET",
            path="/api/vocabulary/topics/{{topic_id}}/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-LRN-PRACTICE-CREATE-001",
            folder="LEARNING",
            name="Create practice session",
            method="POST",
            path="/api/learning/sessions/practice/",
            auth=True,
            body={"topic_id": "{{topic_id}}"},
            expected_status=[200],
            db_check="learning_learningsession and learning_question rows created",
            rollback_scope="Delete seeded user sessions",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                "pm.expect(data).to.have.property('session_id');",
                "pm.environment.set('practice_session_id', data.session_id);",
            ],
        ),
        TestCase(
            case_id="TC-LRN-SESSION-GET-001",
            folder="LEARNING",
            name="Get practice session",
            method="GET",
            path="/api/learning/sessions/{{practice_session_id}}/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-LRN-SESSION-DETAIL-001",
            folder="LEARNING",
            name="Get practice session detail",
            method="GET",
            path="/api/learning/sessions/{{practice_session_id}}/detail/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-LRN-QUESTIONS-GET-001",
            folder="LEARNING",
            name="Get session questions",
            method="GET",
            path="/api/learning/sessions/{{practice_session_id}}/questions/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                "pm.expect(data).to.have.property('questions');",
                "pm.expect(data.questions.length).to.be.above(0);",
                "pm.environment.set('question_id', data.questions[0].id);",
            ],
        ),
        TestCase(
            case_id="TC-LRN-ANSWER-SUBMIT-001",
            folder="LEARNING",
            name="Submit answer",
            method="POST",
            path="/api/learning/sessions/{{practice_session_id}}/submit-answer/",
            auth=True,
            body={"question_id": "{{question_id}}", "answer": 0, "time_spent": 1.5},
            expected_status=[200],
            db_check="learning_useranswer row created/updated",
            rollback_scope="Delete seeded user sessions",
        ),
        TestCase(
            case_id="TC-LRN-SESSION-COMPLETE-001",
            folder="LEARNING",
            name="Complete session",
            method="POST",
            path="/api/learning/sessions/{{practice_session_id}}/complete/",
            auth=True,
            body={},
            expected_status=[200],
            db_check="session completed, progress rows updated",
            rollback_scope="Delete seeded user sessions/progress rows",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                "pm.expect(data).to.have.property('session_id');",
                "pm.environment.set('completed_session_id', data.session_id);",
            ],
        ),
        TestCase(
            case_id="TC-LRN-SESSION-HISTORY-001",
            folder="LEARNING",
            name="Get session history",
            method="GET",
            path="/api/learning/sessions/history/?limit=5",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-LRN-REVIEW-CREATE-001",
            folder="LEARNING",
            name="Create review session",
            method="POST",
            path="/api/learning/sessions/review/",
            auth=True,
            body={"total_questions": 1},
            expected_status=[200, 400],
            db_check="review session rows created",
            rollback_scope="Delete seeded user sessions",
        ),
        TestCase(
            case_id="TC-LRN-EXAM-CREATE-001",
            folder="LEARNING",
            name="Create exam session",
            method="POST",
            path="/api/learning/sessions/exam/",
            auth=True,
            body={
                "topic_id": "{{topic_id}}",
                "time_limit": 10,
                "total_questions": 3,
                "pass_score": 50,
            },
            expected_status=[200],
            db_check="exam session and questions created",
            rollback_scope="Delete seeded user sessions",
            tests_extra=[
                "var data = {};",
                "try { data = pm.response.json(); } catch (e) { data = {}; }",
                "pm.expect(data).to.have.property('session_id');",
                "pm.environment.set('exam_session_id', data.session_id);",
            ],
        ),
        TestCase(
            case_id="TC-LRN-EXAM-CANCEL-001",
            folder="LEARNING",
            name="Cancel exam session",
            method="POST",
            path="/api/learning/sessions/{{exam_session_id}}/cancel/",
            auth=True,
            body={},
            expected_status=[200],
            db_check="exam session deleted",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-LRN-PRON-ASSESS-NEG-001",
            folder="LEARNING",
            name="Assess pronunciation without file",
            method="POST",
            path="/api/learning/pronunciation/assess/",
            auth=True,
            body={},
            expected_status=[400],
            db_check="No learning data mutation",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-PRG-STREAK-001",
            folder="PROGRESS",
            name="Get streak",
            method="GET",
            path="/api/progress/streak/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-PRG-UPCOMING-001",
            folder="PROGRESS",
            name="Get upcoming review",
            method="GET",
            path="/api/progress/upcoming-review/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-PRG-OVERVIEW-001",
            folder="PROGRESS",
            name="Get overview",
            method="GET",
            path="/api/progress/overview/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-PRG-DAILY-001",
            folder="PROGRESS",
            name="Get daily progress",
            method="GET",
            path="/api/progress/daily-progress/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-PRG-RECENT-001",
            folder="PROGRESS",
            name="Get recent sessions",
            method="GET",
            path="/api/progress/recent-sessions/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-CHB-CHAT-EMPTY-001",
            folder="CHATBOT",
            name="Chat endpoint with empty message",
            method="POST",
            path="/api/chat/",
            auth=True,
            body={"message": "   "},
            expected_status=[400],
            db_check="No chat message rows created on validation failure",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-CHB-HISTORY-GET-001",
            folder="CHATBOT",
            name="Get chatbot history",
            method="GET",
            path="/api/history/",
            auth=True,
            expected_status=[200],
            db_check="Read-only",
            rollback_scope="None",
        ),
        TestCase(
            case_id="TC-CHB-HISTORY-DELETE-001",
            folder="CHATBOT",
            name="Delete chatbot history",
            method="DELETE",
            path="/api/history/",
            auth=True,
            expected_status=[200],
            db_check="chatbot_chatmessage rows deleted for seeded user",
            rollback_scope="None",
        ),
    ]


def generate_collection(cases: list[TestCase]) -> None:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        grouped.setdefault(case.folder, []).append(_to_postman_item(case))

    collection = {
        "info": {
            "_postman_id": str(uuid.uuid4()),
            "name": "E-Vocab API Regression",
            "description": (
                "Generated Postman suite for E-Vocab API. "
                "Includes auth, learning, progress, chatbot, vocabulary, and allauth interfaces."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [
            {
                "name": folder,
                "item": items,
            }
            for folder, items in grouped.items()
        ],
        "variable": [
            {"key": "suite_name", "value": "E-Vocab API Regression"},
        ],
        "event": [
            {
                "listen": "prerequest",
                "script": {
                    "type": "text/javascript",
                    "exec": [
                        "if (!pm.environment.get('base_url')) {",
                        "  pm.environment.set('base_url', 'http://127.0.0.1:8000');",
                        "}",
                    ],
                },
            }
        ],
    }
    COLLECTION_PATH.write_text(json.dumps(collection, indent=2), encoding="utf-8")


def generate_environment() -> None:
    env = {
        "id": str(uuid.uuid4()),
        "name": "E-Vocab Local",
        "values": [
            {"key": "base_url", "value": "http://127.0.0.1:8000", "enabled": True},
            {"key": "seed_email", "value": "qa_postman@example.com", "enabled": True},
            {"key": "seed_password", "value": "QaPass123!", "enabled": True},
            {"key": "new_password", "value": "QaPass456!", "enabled": True},
            {"key": "registration_password", "value": "QaPass789!", "enabled": True},
            {"key": "registration_email", "value": "", "enabled": True},
            {"key": "registration_username", "value": "", "enabled": True},
            {"key": "access_token", "value": "", "enabled": True},
            {"key": "refresh_token", "value": "", "enabled": True},
            {"key": "reset_uid", "value": "", "enabled": True},
            {"key": "reset_token", "value": "", "enabled": True},
            {"key": "course_id", "value": "900001", "enabled": True},
            {"key": "topic_id", "value": "900001", "enabled": True},
            {"key": "practice_session_id", "value": "", "enabled": True},
            {"key": "question_id", "value": "", "enabled": True},
            {"key": "exam_session_id", "value": "", "enabled": True},
            {"key": "completed_session_id", "value": "", "enabled": True},
        ],
        "_postman_variable_scope": "environment",
        "_postman_exported_at": datetime.now(timezone.utc).isoformat(),
        "_postman_exported_using": "postman/generate_postman_assets.py",
    }
    ENV_PATH.write_text(json.dumps(env, indent=2), encoding="utf-8")


def generate_testcase_csv(cases: list[TestCase]) -> None:
    with TESTCASE_CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "TestCaseID",
                "Module",
                "Method",
                "Endpoint",
                "Name",
                "ExpectedStatus",
                "DBCheck",
                "RollbackScope",
            ]
        )
        for case in cases:
            if isinstance(case.expected_status, list):
                status = "|".join(str(s) for s in case.expected_status)
            else:
                status = case.expected_status
            writer.writerow(
                [
                    case.case_id,
                    case.folder,
                    case.method,
                    case.path,
                    case.name,
                    status,
                    case.db_check,
                    case.rollback_scope,
                ]
            )


def main() -> None:
    cases = _cases()
    generate_collection(cases)
    generate_environment()
    generate_testcase_csv(cases)
    print(f"Generated: {COLLECTION_PATH}")
    print(f"Generated: {ENV_PATH}")
    print(f"Generated: {TESTCASE_CSV_PATH}")


if __name__ == "__main__":
    main()
