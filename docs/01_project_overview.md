# Prospector — Project Overview

## What Is Prospector?

Prospector is a modular, self-hosted lead generation pipeline. It finds businesses, gathers basic information about them, and produces clean, structured output ready for outreach.

It runs on your own hardware. It costs nothing to operate beyond electricity. It does not depend on any third-party SaaS platform for its core pipeline.

The name fits: it goes out, searches the terrain, and brings back what's worth looking at.

---

## Why It Exists

Teras AI needs a repeatable way to find potential clients. Manual searching is slow, inconsistent, and doesn't scale. Hiring someone to do it is premature. Existing tools are expensive, cloud-dependent, or built for large sales teams.

Prospector is built for a solo operator who wants a quiet, reliable machine running in the background — finding leads while they focus on everything else.

---

## Core Principles

**Modular**
Every stage of the pipeline is independent. The part that finds businesses doesn't care how they'll be qualified. The part that qualifies them doesn't care where they were found. You can swap, upgrade, or disable any stage without rebuilding the rest.

**Local-first**
Prospector runs on your server. Data doesn't leave your network unless you choose to send it somewhere. No subscriptions. No usage limits. No vendor dependency for the finder.

**AI-optional**
The core pipeline works without any AI model. A profile that finds every business with a website in Maribor runs without calling an API. AI is a layer you add on top when you want richer qualification — not a requirement to get started.

**Low running cost**
V1 costs nothing beyond electricity. Any AI features in V2+ use bring-your-own-key (BYOK) so you control spend and provider.

**Expandable**
New data sources, qualification logic, and output formats should not require rewriting what already works.

---

## What Prospector Is Not

- It is not a CRM
- It is not an outreach tool (that's Lynqd)
- It is not a real-time monitoring system
- It is not a cloud-hosted service in V1

---

## The Bigger Picture

Prospector feeds Lynqd. Lynqd generates the outreach. Together they form a complete cold outreach pipeline — from finding a business to sending a personalized email and proposal PDF.

Phase 1: Prospector runs standalone, outputs CSV. *(in progress — finder live)*
Phase 2: Prospector output connects directly to Lynqd input.
Phase 3: Prospector becomes a product offered to other consultants and agencies.

---

## Current Build Status

As of v0.3.0:

- **Running:** `pipeline.py`, profiles, Google Maps finder (Playwright), CSV output, logging
- **Next:** Real website live checks and title/description enrichment in `modules/enricher.py`
- **Later:** AI qualifier (V2), scheduling and extra sources (V3)

Entry point: `python pipeline.py --profile <name>`. Python **3.12+**. Primary deployment target: Ubuntu 24.04 server.

---

## Who Built This

Jernej Teraš / Teras AI — Maribor, Slovenia.
Built as an internal tool first. Productized if it proves its value.
