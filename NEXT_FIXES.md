# Next Fixes for the AI Employer Workspace

This roadmap is focused on your product goal: letting each employer spin up and safely run AI workers that can do real employee-like work.

## 1) Fix multi-tenant data boundaries first (critical)

Why this is first:
- Your architecture notes already call out missing tenant isolation as the top risk.
- Several core models are still not scoped to `Business`, which can cause data leakage between employers.

What to fix next:
- Change `BusinessAIWorker.business` from `User` to `Business` so worker instances are organization-owned, not user-owned.
- Add `business` foreign keys to financial entities like `Tenant`, `Lease`, `Payment`, and reports, then enforce all queries by business.
- Add queryset scoping in API views so authenticated users only see objects for their own business.

## 2) Lock down API authorization and object-level access (critical)

Why this is urgent:
- Some endpoints expose global data and do not enforce authentication.

What to fix next:
- Require authentication on business/AI-employer listing and registration endpoints.
- Replace broad `ModelSerializer(fields="__all__")` for business worker creation with explicit writable/read-only fields.
- Add object-level permission checks (owner/business match) before reads/updates/executes.

## 3) Stabilize test execution and CI baseline (high)

Why this matters:
- The current test run fails during collection, so regressions can ship unnoticed.

What to fix next:
- Add missing test/runtime dependency `rest_framework_simplejwt` or remove its usage.
- Normalize Django test bootstrap (avoid app imports before `django.setup()` in test modules).
- Add a minimum CI gate: lint + unit tests + migration check.

## 4) Align “spin up AI worker” workflow with domain model (high)

Why this matters:
- The API says businesses can spin up workers, but persistence and ownership model are still user-centric.

What to fix next:
- Make worker provisioning accept a business context and record per-business config/version.
- Add lifecycle events: provisioned, active, paused, failed, retired.
- Record provisioning/audit metadata for billing and support.

## 5) Add execution safety + observability for autonomous actions (high)

Why this matters:
- For an AI agent replacing employee tasks, reliability and traceability are product-critical.

What to fix next:
- Add execution policy controls per business (autonomous/hybrid/manual approval thresholds).
- Store structured execution logs (inputs, tool actions, outputs, errors, duration, cost).
- Add retry + idempotency keys for async task execution.

## 6) Introduce usage metering and billing primitives (medium)

Why this matters:
- Multi-tenant AI products need per-customer usage/accounting early.

What to fix next:
- Implement usage metrics model (task runs, API calls, tokens, report generation, successful outcomes).
- Track usage by period and business for pricing plans and quota enforcement.

## 7) Define worker capability contracts (medium)

Why this matters:
- As you add multiple worker types, standardized contracts prevent brittle integrations.

What to fix next:
- Define capability schema per AI worker (supported tasks, required input schema, expected outputs).
- Validate payloads before execution and return typed error codes.

## Suggested 2-week execution order

1. Tenant isolation migrations + queryset scoping.
2. Auth/permission hardening on AI employer and AI worker endpoints.
3. Fix tests and establish CI baseline.
4. Worker lifecycle + usage metering foundation.

