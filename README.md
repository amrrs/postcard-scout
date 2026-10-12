# Postcard Scout

**Search. Optimize. Picture the trip.** A source-linked local itinerary optimizer combining SerpApi Google Maps discovery with fal.ai illustrated postcards.

Built for the SerpApi India Hackathon 2026 — Travel & Local Discovery.

[Watch the 66-second local browser demo](https://github.com/amrrs/postcard-scout/releases/tag/demo-v2): live discovery, exact route optimization, Pareto evidence, fal trail illustration and exported provenance.

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

Open http://127.0.0.1:8766. Enter a city, select heritage, nature or art museums, and click Discover places. Choose a planning mode, optimize a three-stop trail, inspect the objective and distance matrix, and illustrate the trail. You can also illustrate an individual returned place. Download the provenance JSON to preserve the search, plan and generation record.

## Meaningful SerpApi usage

Each discovery makes one `google_maps` engine request (`type=search`). Up to six results retain returned `place_id`, title, description, address, rating, reviews and opening status. The selected place must belong to the server's live search result before generation is permitted. The illustration prompt uses its returned title, description and city. Without SerpApi results there is no selection and no postcard generation — search is on the core path.

The app does not invent ratings, venue addresses or hours. Missing fields are reported as unavailable. Maps links use the returned place ID. No search-image assets are copied or repurposed.

## fal.ai integration

Uses the REST queue API for `fal-ai/flux/schnell`, one 4:3 image, four inference steps, safety checker enabled. The local server submits a job, follows returned status/result URLs, and records the request ID, prompt, seed and image URL. The browser polls a local job route, so no API keys are exposed to the client. FAL_API_KEY is also accepted as a key alias.

No LLM is needed: the prompt is deterministically derived from live place metadata. Current published pricing checked October 12, 2026 was $0.003 per megapixel; provider billing may change. Each illustration button click creates one paid generation; discovery consumes one SerpApi search.

## Verification

```bash
python3 -m unittest discover
```

Tests cover returned place provenance, Maps place ID links, prompt disclosure, queue completion, and safety-blocked images. Live verification retrieved six Jaipur heritage places and completed a fal generation. The demo shows the same locally running flow.

## Limits

This is a local prototype, bound to loopback, with in-memory search/job records. Restarting clears them. It is not a multi-user service. Search results are a snapshot and can be outdated; verify with the venue. Generated art is explicitly labeled **AI illustration, not a photograph** and can depict architecture inaccurately. The artwork is inspiration, not visual evidence. The planner optimizes straight-line paths over the returned candidates; it does not model road travel or opening-hour feasibility. The downloaded JSON includes the remote image URL; provider asset retention is outside this app's control. Queue timeout is three minutes and failures are shown without exposing secrets. Do not use a public deployment without authentication, rate limits and durable storage.

## AI disclosure

OpenAI Codex designed, implemented, tested and documented the app. fal.ai FLUX.1 Schnell generates the postcard art. ScreenStudioly recorded and edited the local functionality demo. The project was created October 12, 2026.

License: MIT. External API and model terms apply to their services and outputs.

## Exact route optimization and Pareto tradeoffs

`planner.py` forms a complete geodesic distance graph over up to six live geocoded candidates. It enumerates every three-stop subset and every permutation (6P3 = 120 route evaluations at six candidates). For each subset it selects the exact shortest open path; then it maximizes mean confidence-adjusted rating minus a user-selected distance penalty. Ratings are shrunk toward a 4-star / 50-review prior, making a 5-star listing with one review less influential than a well-reviewed 4.6-star place. The prior and distance weight are transparent assumptions, not learned or validated tourist preferences.

The UI exposes the chosen sequence, full distance matrix, objective, search-order counterfactual for the same chosen stops, and nondominated Pareto alternatives. Balanced, Walkable and Highest rated modes change the quality/distance tradeoff. Generate a three-panel fal illustration of the selected trail and download its complete evidence/optimization/generation record.

Live Jaipur check on October 12, 2026: six candidates, 120 routes, two Pareto alternatives; the selected three-stop path was 2.087 km geodesic vs 2.392 km for those same stops in search-result order (12.7% shorter). Local optimizer runtime in this one sample was 0.183 ms. These are single-run observations, not general performance or real road-distance claims. Five tests include exact-optimum comparison against an independent all-permutations baseline, symmetry/zero-distance checks, Bayesian shrinkage, missing geocodes, queue completion and safety rejection.

**Scope:** exactness applies only to the bounded returned candidate set and stated objective. Straight-line distances omit roads, barriers and transport. No claim of shortest road route, verified walkability, optimal city-wide tour or feasible opening-hour schedule is made. The tool displays hours for human verification. fal art is a separate conceptual output; it is never used as evidence about a place.
