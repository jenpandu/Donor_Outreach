# Donor Outreach Localization Tool

Flask + PostgreSQL backend for managing fundraising campaigns and
donor communications (both inbound and outbound), with automatic translation using
Amazon Translate and language detection using Amazon Comprehend.

Staff can log outreach messages in the organization's working language and
donor can reply in whatever language the donor used. This system handles
translation in both directions automatically, so staff can always read
every reply in their own language.

## Quick Start

**Install:**
```
pip install -e ".[dev]"
```

**Run (local, requires a running Postgres instance and a `.env` file — see Configuration below):**
```
flask --app donor_outreach.app run
```

**Run (containerized, recommended — spins up Postgres and the API together):**
```
docker compose up --build
```

Once running, the API is available at `http://127.0.0.1:5000`.

## Configuration

Copy `.env.example` to `.env` and fill in:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Postgres connection string for the main app database |
| `TEST_DATABASE_URL` | Separate Postgres database used only by the pytest suite |
| `AWS_PROFILE` | Named AWS CLI profile used to authenticate boto3 (see AWS Setup below) |
| `AWS_REGION` | AWS region for Comprehend/Translate calls |
| `LOG_LEVEL` | structlog level (`DEBUG`, `INFO`, etc.) |

## AWS Setup

This project calls two AWS services: **Comprehend** (`DetectDominantLanguage`)
and **Translate** (`TranslateText`). Authentication is via a dedicated,
least-privilege IAM user. It does not have root/admin credentials.

The IAM policy granting only these two actions is committed at
[`iam/comprehend-translate-policy.json`](iam/comprehend-translate-policy.json).

Credentials are given by a named AWS CLI profile (`aws configure --profile <name>`),
referenced by the `AWS_PROFILE` environment variable. Raw access keys are
never stored in `.env` or in code. When running the app with Docker, the host's
`~/.aws` directory is mounted read-only into the `api` container so the
same profile-based credentials work the same in both environments.

## Architecture

- **Flask** app-factory pattern with blueprints (`api/campaigns`, `api/messages`, `api/health`)
- **PostgreSQL** via SQLAlchemy 2.0, with a real Alembic migration history (`migrations/`)
- **Pydantic v2** models validate every request at the HTTP boundary
- **boto3**, wrapped in isolated, injectable client classes (`clients/translate`, `clients/comprehend`)
  so the AWS calls can be stubbed in tests without live credentials
- **structlog** emits one structured JSON log line per request, including a
  per-request correlation ID and duration
- A `DomainError` exception hierarchy (`errors.py`) replaces manual
  `if record is None: return 404` checks — route handlers raise typed
  errors, and a single Flask errorhandler converts them into a consistent
  JSON envelope

## Data Model

See [`docs/erd.md`](docs/erd.md) for the full entity-relationship diagram.

Two entities: `Campaign` (1) → `Message` (many). A message's `direction`
(`outbound`/`inbound`), original text, detected/target language, and
translated text are all explicit, queryable columns — the original text
is always preserved alongside any translation.

## API Overview

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/campaigns` | Dashboard: list all campaigns with message counts by direction |
| `POST` | `/campaigns` | Create a campaign |
| `GET` | `/campaigns/<id>` | Get one campaign |
| `PUT` | `/campaigns/<id>` | Partially update a campaign (name, goal amount, description) |
| `DELETE` | `/campaigns/<id>` | Delete a campaign (cascades to its messages — see below) |
| `GET` | `/campaigns/<id>/messages` | List messages for a campaign; supports `?direction=`, `?language=`, `?sort=` |
| `POST` | `/campaigns/<id>/messages/outbound` | Log an outreach message; translates into the donor's preferred language |
| `POST` | `/campaigns/<id>/messages/inbound` | Log a donor reply; detects its language and translates into the org's default |
| `GET` | `/campaigns/<id>/inbox` | All inbound messages for a campaign, already translated |
| `GET` | `/messages/<id>` | Get one message |
| `PUT` | `/messages/<id>` | Correct a message's original text (re-triggers translation — see below) |
| `DELETE` | `/messages/<id>` | Delete a message |
| `GET` | `/live` | Liveness check |
| `GET` | `/ready` | Readiness check (verifies the database is reachable; does *not* check Comprehend/Translate — see below) |

## Documented Edge Case Decisions

**Deleting a campaign cascades to its messages.**
`ON DELETE CASCADE` is set at the database level on `Message.campaign_id`,
mirrored by `cascade="all, delete-orphan"` on the ORM relationship. Deleting
a campaign is a destructive operation that also removes its full message
history — there is no soft-delete or archival step. This keeps the data
model simple and avoids orphaned messages pointing at a campaign that no
longer exists.

**Editing a message's original text re-triggers translation.**
Correcting `original_text` via `PUT /messages/<id>` automatically re-runs
the translation pipeline. So, outbound messages are re-translated from the
org's default language into the message's existing target language;
inbound messages are re-run through Comprehend (since a text correction
could change the detected language) and then re-translated into the org's
default. A stale translation next to a corrected original text was decided to be
more likely to mislead staff than the cost of an extra API call.

**Comprehend or Translate being unavailable does not block logging a message.**
If either AI call fails (network issue, throttling, service outage), the
message still saves with its original text intact — `translated_text` is
left `null` rather than the whole request being rejected. A donor's
outreach message or reply should never be lost because of a transient AWS
issue; translation can be retried later. This applies both at message
creation and at edit-triggered re-translation.

**A donor's preferred language matching the org's default skips translation.**
When an outbound message's `target_language` equals the campaign's
`def_lang` (or, for inbound, when the detected language matches it), no
Translate call is made — `translated_text` is set directly to the original
text. Calling Translate to convert a language into itself is unnecessary.

**Low-confidence language detection falls back to the campaign's default language.**
Comprehend's `DetectDominantLanguage` can return low confidence on very
short text (e.g. `"Gracias!"`). When the top result's confidence score is
below `0.5`, the system assumes the reply is in the organization's own
default language rather than trusting an uncertain confidence score. The same
fallback applies if the Comprehend call itself fails outright.

**A campaign's default language (`def_lang`) is fixed once set.**
It is purposely excluded from `CampaignUpdate` and can't be changed
with `PUT /campaigns/<id>`. Existing messages' translations are relative to
whatever `def_lang` was in effect at the time they were created; allowing
it to change later would leave old translations silently inconsistent
with a new default.

**`/ready` does not check Comprehend/Translate reachability.**
Readiness only checks the database connection. Most of this application
(campaign and message CRUD) works with no dependency on AWS at all, so an
AWS outage should not make the whole service report itself as unready.
Per-request AI failures are instead handled by the graceful degradation
described above.

**Deletion confirmation is via the resource ID in the URL path**, not the
request body (e.g. `DELETE /campaigns/<id>`, not `DELETE /campaigns` with
an ID in the body). This keeps delete requests consistent with the
GET/PUT routes for the same resource, at the cost of diverging from a
body-based confirmation pattern.

**Invalid input at the HTTP boundary** is caught by Pydantic and returns a
`422` with a field-by-field error envelope (`{"error": "validation_failed", "detail": [...]}`),
via a dedicated Flask errorhandler for `pydantic.ValidationError`, separate
from the `DomainError` hierarchy used for application-level errors like
`404 Not Found`.

**Concurrent mutations** are handled by SQLAlchemy's default session/transaction
behavior: two staff members updating the same message will both succeed,
with the second write overwriting the first (last-write-wins) — there is
no optimistic locking or version column in the current schema. A campaign
deleted while a message against it is mid-request would either complete
its `CASCADE` delete first (removing the message) or the message write
would complete first and then be removed by the subsequent cascade;
no explicit conflict-detection is implemented for this race.

**Message-logging endpoints are rate-limited to 10 requests per minute per client IP.**
`POST /campaigns/<id>/messages/outbound` and `.../inbound` are throttled via
Flask-Limiter, keyed by client IP address. Message logging is a manual,
deliberate staff action rather than a bulk or automated operation, so 10
per minute comfortably accommodates normal use while guarding against
accidental request loops or abuse.
## Testing

```
pytest
```

15+ tests cover campaign and message CRUD (happy and error paths), health
checks, and the Comprehend/Translate client wrappers using
`botocore.stub.Stubber` — no live AWS credentials or network access
required to run the suite. Tests run against a separate database
(`TEST_DATABASE_URL`), created and torn down fresh for every test.
