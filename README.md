# Filtered AI conference deadlines

Calendar subscription for ML, CV, SP, AP, HCI and MISC. Matches any selected subject and includes paper and abstract submission deadlines. Source: http://aideadlines.org/ (derived from https://github.com/paperswithcode/ai-deadlines).

GitHub Actions refreshes the feed daily at 02:17 UTC. GitHub Pages serves `deadlines.ics`. Invalid/unannounced dates are skipped; event time zones are preserved. A failed refresh leaves the published feed intact. See Actions for failures and `status.json` for the last successful refresh.

Run `python3 build.py` to regenerate. Python 3.9+; no external dependencies.
