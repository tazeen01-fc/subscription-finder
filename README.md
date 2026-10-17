# Subscription Finder

A small web app that reads a bank transactions CSV, finds recurring monthly
subscriptions, shows what each costs per year, and asks an AI for saving ideas.

## What it does
- Upload a CSV with the columns: date, description, amount
- Detects charges that repeat about every month (3 or more times)
- Shows a table and the total yearly cost of subscriptions
- Sends only the merchant names and prices (never the whole CSV) to an AI
  model through the Groq API and shows short saving tips

## Tech used
Python, Streamlit, Groq API (free tier)

## How to run it
1. Install Python 3.
2. Install the packages: `pip install streamlit groq`
3. Get a free API key at console.groq.com
4. Run: `streamlit run app.py`
5. Upload a CSV, paste your key in the password box, and click "Get AI tips"

## Example CSV
```
date,description,amount
2026-06-03,Netflix,15.99
2026-07-03,Netflix,15.99
2026-08-03,Netflix,15.99
```

## Notes
- The API key is typed into the page and is never saved in the code.
- AI tips can be wrong or made up, so check them before acting on them.
- Only monthly subscriptions are detected for now.
