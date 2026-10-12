# Postcard Scout

**Discover real places, then picture the trip.** A local travel inspiration tool combining SerpApi Google Maps discovery with fal.ai illustrated postcards.

Built for the SerpApi India Hackathon 2026 — Travel & Local Discovery.

## Why it exists

Travel inspiration often starts with invented or generic imagery and a separate search for real places. Postcard Scout starts with a live shortlist: the user sees actual place names, addresses, ratings, review counts and opening status, verifies a Maps link, and chooses a returned place before generating an illustration. A source-linked JSON trip card preserves the evidence and generation record.

## Run locally

Python 3.9+; standard library only. No dependencies to install.

```bash
git clone https://github.com/amrrs/postcard-scout.git
cd postcard-scout
cp .env.example .env
# Edit .env with SERPAPI_API_KEY and FAL_KEY (never commit keys).
python3 app.py
```

Open http://127.0.0.1:8766. Enter a city, select heritage, nature or art museums, and click Discover places. Choose Illustrate this place, inspect the source/generation record, and download the trip card.

## Meaningful SerpApi usage

Each discovery makes one `google_maps` engine request (`type=search`). Up to six results retain returned `place_id`, title, description, address, rating, reviews and opening status. The selected place must belong to the server's live search result before generation is permitted. The illustration prompt uses its returned title, description and city. Without SerpApi results there is no selection and no postcard generation — search is on the core path.

The app does not invent ratings, venue addresses or hours. Missing fields are reported as unavailable. Maps links use the returned place ID. No search-image assets are copied or repurposed.

## fal.ai integration

Uses the REST queue API for `fal-ai/flux/schnell`, one 4:3 image, four inference steps, safety checker enabled. The local server submits a job, follows returned status/result URLs, and records the request ID, prompt, seed and image URL. The browser polls a local job route, so no API keys are exposed to the client. FAL_API_KEY is also accepted as a key alias.

No LLM is needed: the prompt is deterministically derived from live place metadata. Current published pricing checked October 12, 2026 was $0.003 per megapixel; provider billing may change. Each illustration button click creates one paid generation; discovery consumes one SerpApi search.

## Verification

```bash
python3 -m unittest test_app
```

Tests cover returned place provenance, Maps place ID links, prompt disclosure, queue completion, and safety-blocked images. Live verification retrieved six Jaipur heritage places and completed a fal generation. The demo shows the same locally running flow.

## Limits

This is a local prototype, bound to loopback, with in-memory search/job records. Restarting clears them. It is not a multi-user service. Search results are a snapshot and can be outdated; verify with the venue. Generated art is explicitly labeled **AI illustration, not a photograph** and can depict architecture inaccurately. It is inspiration, not visual evidence or a route planner. The downloaded JSON includes the remote image URL; provider asset retention is outside this app's control. Queue timeout is three minutes and failures are shown without exposing secrets. Do not use a public deployment without authentication, rate limits and durable storage.

## AI disclosure

OpenAI Codex designed, implemented, tested and documented the app. fal.ai FLUX.1 Schnell generates the postcard art. ScreenStudioly recorded and edited the local functionality demo. The project was created October 12, 2026.

License: MIT. External API and model terms apply to their services and outputs.
