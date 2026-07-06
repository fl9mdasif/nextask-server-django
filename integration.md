# Integration & Unit Tests — NexTask Backend

> **Test Suite Documentation**
> Django backend for Vai Radiology LLC assignment.
> All 28 tests pass with zero failures.

---

## Overview

This document describes the automated test suite written for the NexTask Django REST API backend. Tests cover model integrity, API endpoint behavior, authentication flows, and data isolation between users.

| Metric | Value |
|---|---|
| Total tests | 28 |
| Test runner | `python manage.py test` |
| Test framework | Django `TestCase` + DRF `APITestCase` |
| Database | In-memory SQLite (isolated per run) |
| Auth scheme | JWT (Bearer token via `djangorestframework-simplejwt`) |
| Result | ✅ **28 passed, 0 failed** |

---

## Running the Tests

### Prerequisites

```bash
# Activate virtual environment
venv\Scripts\activate          # Windows PowerShell
source venv/bin/activate       # Mac / Linux
```

### Run all tests

```bash
python manage.py test tasks users
```

### Run with verbose output

```bash
python manage.py test tasks users --verbosity=2
```

### Run a single test class

```bash
python manage.py test tasks.tests.TaskModelTest
python manage.py test tasks.tests.TaskAPITest
python manage.py test users.tests.AuthAPITest
```

### Run a single test method

```bash
python manage.py test tasks.tests.TaskAPITest.test_create_task_returns_201
```

---

## Test Files

| File | Class | Tests |
|---|---|---|
| `tasks/tests.py` | `TaskModelTest` | 6 |
| `tasks/tests.py` | `TaskAPITest` | 13 |
| `users/tests.py` | `AuthAPITest` | 9 |

---

## 1. Task Model Tests (`TaskModelTest`)

**File:** `tasks/tests.py`
**Base class:** `django.test.TestCase`
**Purpose:** Verify the `Task` model stores data correctly, applies default values, and returns the right string representation.

| Test Method | What It Verifies |
|---|---|
| `test_task_creation_stores_all_fields` | All fields (title, priority, status, due_date, tags, user) are persisted correctly on creation |
| `test_task_default_priority_medium` | `priority` defaults to `"medium"` when not provided |
| `test_task_default_status_todo` | `status` defaults to `"todo"` when not provided |
| `test_task_default_order_zero` | `order` defaults to `0` when not provided |
| `test_task_default_tags_empty_list` | `tags` defaults to an empty list `[]` when not provided |
| `test_task_str_returns_title` | `str(task)` returns the task's title |

---

## 2. Task API Tests (`TaskAPITest`)

**File:** `tasks/tests.py`
**Base class:** `rest_framework.test.APITestCase`
**Purpose:** Verify every Task API endpoint — create, list, filter, update, delete, reorder — behaves correctly for authenticated users and rejects unauthorized access.

**Setup:** Each test creates a user, logs in via `POST /api/auth/login/`, and sets the JWT `Bearer` token on all requests.

### Create

| Test Method | What It Verifies |
|---|---|
| `test_create_task_returns_201` | Valid POST returns `201 Created` with `success: true` and correct data |
| `test_create_task_saves_to_db` | Created task is actually persisted in the database |
| `test_create_task_missing_title_returns_400` | Missing required `title` field returns `400 Bad Request` |

### List & Filter by Date

| Test Method | What It Verifies |
|---|---|
| `test_list_tasks_returns_only_matching_date` | `?date=` query param filters tasks to the given date only |
| `test_list_tasks_without_date_returns_all_user_tasks` | Omitting `?date=` returns all tasks belonging to the user |
| `test_list_tasks_does_not_return_other_users_tasks` | Tasks belonging to another user are never exposed |

### Update (PATCH)

| Test Method | What It Verifies |
|---|---|
| `test_patch_task_updates_title_and_status` | PATCH correctly updates `title` and `status` fields |
| `test_patch_task_partial_update_preserves_other_fields` | Updating one field does not overwrite unrelated fields |
| `test_patch_other_users_task_returns_404` | Attempting to PATCH another user's task returns `404 Not Found` |

### Delete

| Test Method | What It Verifies |
|---|---|
| `test_delete_task_returns_200_and_removes_from_db` | DELETE returns `200 OK` and removes the task from the database |
| `test_delete_other_users_task_returns_404` | Attempting to DELETE another user's task returns `404` and leaves it in the DB |

### Reorder (Drag & Drop)

| Test Method | What It Verifies |
|---|---|
| `test_reorder_updates_status_and_order` | `PATCH /tasks/:id/reorder/` updates both `status` and `order` correctly |

### Authentication Guard

| Test Method | What It Verifies |
|---|---|
| `test_unauthenticated_request_returns_401` | Requests without a Bearer token are rejected with `401 Unauthorized` |

---

## 3. Auth API Tests (`AuthAPITest`)

**File:** `users/tests.py`
**Base class:** `rest_framework.test.APITestCase`
**Purpose:** Verify the login, logout, and `/me` endpoints behave correctly using the custom email-based `User` model.

### Login

| Test Method | What It Verifies |
|---|---|
| `test_login_with_correct_credentials_returns_200` | Valid email + password returns `200 OK` with `success: true` |
| `test_login_response_contains_access_and_refresh_tokens` | Response includes non-empty `access` and `refresh` JWT strings |
| `test_login_response_contains_user_info` | Response includes `id`, `username`, and `email` of the logged-in user |
| `test_login_with_wrong_password_returns_401` | Wrong password returns `401 Unauthorized` with `success: false` |
| `test_login_with_nonexistent_email_returns_401` | Unknown email returns `401 Unauthorized` |
| `test_login_with_wrong_password_does_not_return_token` | Failed login response does not contain any token |

### Me Endpoint

| Test Method | What It Verifies |
|---|---|
| `test_me_returns_current_user_when_authenticated` | `GET /api/auth/me/` returns the logged-in user's data with a valid token |
| `test_me_returns_401_when_unauthenticated` | `GET /api/auth/me/` without a token returns `401 Unauthorized` |

### Logout

| Test Method | What It Verifies |
|---|---|
| `test_logout_with_valid_refresh_token_returns_200` | `POST /api/auth/logout/` with a valid refresh token blacklists it and returns `200 OK` |

---

## Test Design Decisions

### 1. Custom User model
All tests use `get_user_model()` instead of importing `User` directly. This correctly resolves the custom `users.User` model which uses `email` as the `USERNAME_FIELD`.

### 2. JWT authentication in tests
Tests authenticate by calling the real `POST /api/auth/login/` endpoint (not by mocking), then set `HTTP_AUTHORIZATION: Bearer <token>` via `self.client.credentials()`. This tests the full auth flow end-to-end.

### 3. User isolation tests
Every mutation endpoint (PATCH, DELETE) is tested with a task belonging to a different user to confirm the API returns `404` rather than leaking data or allowing unauthorized modification.

### 4. Database isolation
Each test class gets a fresh in-memory SQLite database spun up and torn down automatically by Django's test runner. No test data leaks between tests.

---

## Expected Output

```
Found 28 test(s).

test_create_task_missing_title_returns_400 ... ok
test_create_task_returns_201 ... ok
test_create_task_saves_to_db ... ok
test_delete_other_users_task_returns_404 ... ok
test_delete_task_returns_200_and_removes_from_db ... ok
test_list_tasks_does_not_return_other_users_tasks ... ok
test_list_tasks_returns_only_matching_date ... ok
test_list_tasks_without_date_returns_all_user_tasks ... ok
test_patch_other_users_task_returns_404 ... ok
test_patch_task_partial_update_preserves_other_fields ... ok
test_patch_task_updates_title_and_status ... ok
test_reorder_updates_status_and_order ... ok
test_unauthenticated_request_returns_401 ... ok
test_task_creation_stores_all_fields ... ok
test_task_default_order_zero ... ok
test_task_default_priority_medium ... ok
test_task_default_status_todo ... ok
test_task_default_tags_empty_list ... ok
test_task_str_returns_title ... ok
test_login_response_contains_access_and_refresh_tokens ... ok
test_login_response_contains_user_info ... ok
test_login_with_correct_credentials_returns_200 ... ok
test_login_with_nonexistent_email_returns_401 ... ok
test_login_with_wrong_password_does_not_return_token ... ok
test_login_with_wrong_password_returns_401 ... ok
test_logout_with_valid_refresh_token_returns_200 ... ok
test_me_returns_401_when_unauthenticated ... ok
test_me_returns_current_user_when_authenticated ... ok

----------------------------------------------------------------------
Ran 28 tests in 88.749s

OK
```

> **Note:** The `UserWarning: No directory at staticfiles/` message is harmless — WhiteNoise logs this locally because `collectstatic` hasn't been run yet. It does not affect test results. Run `python manage.py collectstatic` before deploying to PythonAnywhere.
