# Neighborhood Connect — Streamlit

Public Houston Super Neighborhood directory prepared for GitHub user **Sandysmile**.
This is a Streamlit recreation of the directory design, not a pixel-identical export of the Sites app.

## Publish using the GitHub website

1. Sign in at https://github.com and create a repository named `neighborhood-connect-streamlit` under **Sandysmile**.
2. Extract this ZIP. Upload the contents of its `neighborhood-connect-streamlit` folder into the repository root using **Add file → Upload files**. Make sure `app.py`, `data_source.py`, `style.css`, `requirements.txt`, and `data_snapshot.json` appear at the root. Include `.streamlit/config.toml` for theme styling (optional if hidden files are difficult to upload).
3. Commit the files to the `main` branch.
4. Open https://share.streamlit.io and sign in with your GitHub account.
5. Choose **Create app**, select repository `Sandysmile/neighborhood-connect-streamlit`, branch `main`, and main file `app.py`.
6. Select **Deploy**. Streamlit returns the actual app URL; no app is deployed by this ZIP itself.

## Local run

Python 3.11 or newer recommended.

```sh
pip install -r requirements.txt
streamlit run app.py
```

## Data and workflow

- Live source
- CKAN DataStore resource: `6ee89d61-bd53-48a1-b611-3208d1844e16`.
- Live responses are cached for 15 minutes.
- If the source is unavailable, the app shows a warning and uses the bundled November 2, 2026 snapshot (88 records). This is a fixed fallback, not a continuously updated backup.
- This app is read-only. DON/IT editing stays in your Power Apps application. No staff credentials, SharePoint secrets, editing permissions, or staff-only records are included.
- Edits to SharePoint are not automatically reflected here. Publish approved changes to the Open Data resource through your separate integration first.
- Email and website buttons appear only when usable contact information is present. Bare website and Facebook URLs gain an HTTPS prefix.
- The app does not yet include address geocoding or boundary lookup.

## Validation

The package includes automated tests for record counts, filtering, URL handling, field cleanup, live data paging, and fallback behavior. Run `python -m unittest -v`.
Validated November 3, 2026: five data tests passed; Streamlit AppTest passed initial rendering, search, the details dialog, and email links using a simulated portal outage. The live sandbox API also returned 88 records. Tested with Streamlit 1.66.1. The deployed interface must still be checked after deployment; no Streamlit deployment or browser visual verification is claimed.
