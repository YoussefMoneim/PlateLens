# PlateLens — Interactive Demo

A standalone, zero-dependency showcase of the PlateLens multi-agent pipeline.

**Why this exists:** the full app calls IBM WatsonX, which needs an API key and costs money per run. This demo lets anyone experience what PlateLens does — the agent pipeline, the dietary filtering, the recipe and nutrition outputs — without any key, any backend, or any cost. The outputs shown are real results captured from local runs of the actual app, then baked into a static page.

It's a single `index.html` file. No build step, no install.

## Run it locally

Just open `index.html` in any browser. That's it.

## Deploy it free on GitHub Pages

1. Push this repo to GitHub (already done if you're reading this there).
2. Go to the repo **Settings → Pages**.
3. Under "Build and deployment", set **Source: Deploy from a branch**.
4. Choose branch `main` and folder `/ (root)` — or set the folder to `/demo` if Pages supports it in your setup. Simplest path: copy `demo/index.html` to the repo root as `index.html` and point Pages at root.
5. Save. In ~1 minute your demo is live at `https://youssefmoneim.github.io/PlateLens/`.

## What's a demo vs. the real app

| | Demo (`/demo`) | Full app (`/app.py`) |
|---|---|---|
| Runs | In the browser, static | Locally with Gradio |
| Needs API key | No | Yes (IBM WatsonX) |
| Data | Real outputs, pre-captured | Live, from your own photos |
| Purpose | Let anyone see it work | Actually process new images |
