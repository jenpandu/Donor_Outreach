# Nonprofit Donor Outreach Localization Tool

## Objective

Develop a donor-communications backend for a nonprofit running
international fundraising campaigns, where staff write outreach messages
in one language but donors reply in whatever language they're most
comfortable in — leaving staff either guessing at replies or pasting text
into a translator by hand before they can respond. The system should make
it easy to manage campaigns and log donor communications in both
directions, automatically translating outbound messages into each donor's
preferred language and automatically detecting and translating inbound
replies back into the organization's working language via **Amazon
Translate** and **Amazon Comprehend** — so staff always read every reply
in their own language, no matter what language it arrived in. Prioritize
correctness on the data layer — a message's direction, detected language,
and translation are explicit, queryable fields, with the original text
always preserved alongside the translation. The deliverable is a
containerized service that runs locally via `docker compose up` and
exposes a documented REST API, backed by a real PostgreSQL database and
real (in production) calls to two chained AWS managed AI services.

## Functional Requirements

### Campaign Management

- **Add New Campaign:**
  - Staff should be able to create a new fundraising campaign by
    specifying its name, goal amount, description, and the organization's
    default working language.
- **View Campaigns:**
  - Provide a dashboard endpoint listing all campaigns with their core
    metadata and message count broken down by direction.
- **Edit Campaign:**
  - Allow updating a campaign's name, goal amount, or description.
- **Delete Campaign:**
  - Implement deletion with a confirmation requirement (such as requiring
    the campaign id in the request body). Decide (and document in your
    README) whether deleting a campaign cascades to delete its messages.

### Donor Message Management

- **Log Outbound Message:**
  - Staff should be able to log an outreach message to a donor by
    specifying the message text (in the organization's default language),
    the donor's name, and the donor's preferred language.
- **Log Inbound Message:**
  - Staff should be able to log a donor's reply by specifying the message
    text (in whatever language the donor wrote it) and the donor's name.
- **View Messages for a Campaign:**
  - List all messages for a campaign, including direction, original text,
    detected/target language, and translated text, with filter support by
    direction and language.
- **Edit Message:**
  - Allow correcting a message's original text after logging. Decide (and
    document in your README) whether this re-triggers translation.
- **Delete Message:**
  - Implement deletion with a confirmation requirement (such as requiring
    the message id in the request body).

### API Design & Developer Experience

- **Consistent Error Envelopes:**
  - All errors (validation, not-found, conflict, upstream AI-service
    failure) should return a consistent JSON shape with an error code,
    human-readable message, and request_id.
- **Liveness and Readiness:**
  - Expose `/live` and `/ready` endpoints. `/live` confirms the process is
    up; `/ready` confirms downstream dependencies (the database) are
    reachable. Comprehend/Translate reachability is *not* part of
    `/ready` — see Edge Case Handling below.
- **Structured Request Logging:**
  - Every request should emit a structured log line containing method,
    path, status code, duration, and correlation id, as machine-parseable JSON.
- **Filtered Listings:**
  - List endpoints should support filter + sort query parameters across
    `direction`, `language`, and message date.

### Edge Case Handling

- **Comprehend or Translate Is Unavailable:**
  - Decide how message logging behaves if language detection or
    translation fails. Should the message still save with the original
    text only (translation attempted lazily on next read), or should
    logging be rejected outright? Document your choice and reasoning.
- **Donor's Preferred Language Equals the Org's Default Language:**
  - Decide how an outbound message behaves when no translation is
    actually needed — calling Translate anyway (wasteful but simple) or
    short-circuiting to store the original text as both fields. Document your choice.
- **Very Short Donor Reply for Language Detection:**
  - A short reply like `"Gracias!"` may not give Comprehend enough signal
    to confidently detect a language. Decide on a confidence threshold
    below which you fall back to a default assumption, and document it.
- **Invalid Input at the HTTP Boundary:**
  - Pydantic should validate every request body at the boundary and
    return a 422 with a clear field-by-field error envelope on malformed
    input (e.g., a negative goal amount).
- **Concurrent Mutations:**
  - Describe what happens if two staff members log a reply from the same
    donor at the same time, or a campaign is deleted while a message
    against it is still being translated. Document the expected behavior.

### AI-Assisted Feature (Required)

> **Sequencing — build this last.** This feature is a required, graded
> part of the deliverable, not an optional stretch goal. Implement it only
> after the core CRUD service is complete and working end to end — the AI
> pipeline should be layered on top of a finished functional deliverable,
> not built in parallel with it. A complete core with the AI feature added
> last scores well; an AI pipeline bolted onto an incomplete or broken core
> does not.

- **Outbound Translation:**
  - When an outbound message is logged, call Translate's `TranslateText`
    to render it into the donor's preferred language and store the result
    alongside the original.
- **Inbound Language Detection and Translation:**
  - When an inbound reply is logged, call Comprehend's
    `DetectDominantLanguage` to identify what language it's written in,
    then call Translate's `TranslateText` to render it into the
    organization's default working language.
- **Always-Translated Inbox:**
  - Add `GET /campaigns/{id}/inbox` returning every inbound message
    already translated into the organization's default language by
    default — the actual "staff always read every reply in their own
    language" payoff from the Objective, not a translation staff have to
    remember to request per message.
- **Isolated, Mockable AWS Clients:**
  - Both the Comprehend and Translate calls must go through their own
    single, injectable client modules (mirroring the shared-session
    pattern from this course's Week 3 boto3 material) so your test suite
    can substitute fake/mocked clients and run without live AWS credentials.

## Stretch Goals

Stretch goals are features you want to add to an application, but they
aren't required. For this project, Stretch Goals are a way to go above and
beyond the minimum requirements and I look forward to seeing what unique
features you will add to your project. Here are some examples you might consider:

- **Deploy the App to AWS:**
  - Push your Docker image to Amazon ECR and run the stack on an AWS
    compute service of your choice (App Runner, ECS, or an EC2 instance).
    Document your deployment architecture and any cost/cleanup considerations.
- **Bedrock-Powered Reply Drafts:**
  - Add an endpoint that sends a translated donor reply to a foundation
    model via Bedrock's Converse API and drafts a suggested response in
    the organization's default language, ready for a staff member to
    review and send. This uses content not yet covered in lecture at the
    time this project is assigned — a good stretch goal for anyone who
    wants to explore ahead.
- **SageMaker Custom Model:**
  - Train a simple custom model that predicts donor re-engagement
    likelihood from message sentiment/frequency features, hosted behind a
    SageMaker endpoint. Also beyond the current curriculum — a good "go
    deeper" option.
- **Rate Limiting:**
  - Add Flask-Limiter to throttle message logging per client IP. Choose a
    sensible limit and document why in your README.
- **Second Entity Relationship:**
  - Extend the model to support a `Donor` entity — a persistent donor
    record across multiple campaigns, with a preferred language stored once.
- **Minimal Web UI:**
  - Add a single HTML page (or React app) that consumes your API and
    displays a campaign's translated inbox for staff.
- **Persistent Audit Log:**
  - Record every mutation (create / update / delete) into an audit table
    with timestamp, action, entity, and actor.
- **Bulk Import:**
  - Add an endpoint that accepts a CSV of historical donor messages and
    inserts them for a campaign in one transaction, with all-or-nothing semantics.
- **Sentiment-Aware Reply Flagging:**
  - Run Comprehend's `DetectSentiment` on translated inbound messages and
    flag negative-sentiment replies for priority staff follow-up.

## Technical Requirements

Must be a backend solution consisting of:

- Python 3.11+
- Flask 3.x with the app-factory pattern and blueprints
- Pydantic v2 for HTTP-boundary validation
- PostgreSQL via SQLAlchemy 2.0 and Flask-Migrate, with a real migration
  history checked into the repo (no `create_all()` in production code paths)
- boto3, authenticated via a dedicated, least-privilege IAM user (never
  root/admin credentials) — the IAM policy JSON granting only
  `comprehend:DetectDominantLanguage` and `translate:TranslateText` must be
  committed to the repo
- Separate, injectable client wrapper modules for Comprehend and
  Translate — not `boto3.client(...)` called ad hoc from route handlers
- structlog for structured JSON logging with per-request correlation IDs
- pytest with fixtures and parametrize for the test suite; AWS calls must
  be mocked/stubbed in tests (e.g. `unittest.mock` or `botocore.stub.Stubber`)
  so the suite runs without live AWS credentials or network access
- Docker multi-stage Dockerfile + docker-compose.yml for a local
  api + db stack, with a database health check gating the API's startup
- pyproject.toml with a src/ layout and a `[project.optional-dependencies]` dev block
- Code should be available in a private GitHub repository, with the
  instructor added as a collaborator
- Possesses all required CRUD functionality
- Handles edge cases effectively

## Non-Functional Requirements

- Well-documented code (module docstrings + function docstrings on public surfaces)
- Code upholds industry best practices (SOLID / DRY / single-responsibility)
- Type hints on every function signature
- Test coverage on happy + error paths (at least 15 pytest tests, including
  at least one test per Comprehend- and Translate-backed endpoint using
  mocked clients)
- Structured logs (no print statements in production code paths)
- Container runnable via a single `docker compose up`
- README with one-line install and one-line run instructions, plus your
  documented decisions for every Edge Case Handling item above
- Pydantic models have explicit field constraints (Literal types, min/max
  length, ge on goal amount)
- No mutable default arguments; use `field(default_factory=...)` for collections
- Errors raise typed exceptions from a DomainError hierarchy, not generic Exception
- Data model documented as an entity-relationship diagram (ERD) — every
  entity, its fields, and the cardinality of each relationship — checked
  into the repository
- A kanban board with a complete, prioritized backlog is set up **before
  development begins**; work is pulled from the board rather than started ad hoc