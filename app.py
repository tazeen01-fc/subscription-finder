import csv
import io
from datetime import datetime

import streamlit as st
import pandas as pd
from groq import Groq

MODEL = "openai/gpt-oss-20b"


def read_date(text):
    for style in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, style)
        except ValueError:
            pass
    raise ValueError("Unknown date format: " + text)


def find_subscriptions(csv_text):
    charges = {}
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        merchant = row["description"].strip().title()
        day = read_date(row["date"])
        amount = float(row["amount"])
        charges.setdefault(merchant, []).append((day, amount))

    results = []
    for merchant in charges:
        items = sorted(charges[merchant])
        if len(items) < 3:
            continue

        gaps = []
        for i in range(1, len(items)):
            gaps.append((items[i][0] - items[i - 1][0]).days)

        if all(27 <= gap <= 33 for gap in gaps):
            monthly = items[-1][1]
            results.append({
                "Merchant": merchant,
                "Monthly": monthly,
                "Per year": round(monthly * 12, 2),
            })
    return results


st.title("Subscription Finder")

uploaded = st.file_uploader("Upload your transactions CSV", type="csv")

if uploaded is not None:
    csv_text = uploaded.getvalue().decode("utf-8-sig")
    subs = find_subscriptions(csv_text)

    if subs:
        rows = []
        for s in subs:
            rows.append({
                "Merchant": s["Merchant"],
                "Monthly": f"{s['Monthly']:.2f}",
                "Per year": f"{s['Per year']:.2f}",
            })
        st.table(rows)

        total = sum(s["Per year"] for s in subs)
        st.metric("Total subscriptions per year", f"{total:.2f}")
        chart_data = pd.DataFrame(
            {"Per year": [s["Per year"] for s in subs]},
            index=[s["Merchant"] for s in subs],
            )
        st.bar_chart(chart_data)

        st.subheader("AI saving tips")
        api_key = st.text_input("Paste your Groq API key", type="password")
        currency = st.text_input("Currency symbol", value="$")

        if st.button("Get AI tips"):
            if not api_key:
                st.warning("Please paste your API key first.")
            else:
                summary = "\n".join(
                    f"- {s['Merchant']}: {s['Monthly']:.2f} per month "
                    f"({s['Per year']:.2f} per year)"
                    for s in subs
                )
                system_message = (
                    "You are a friendly money-saving assistant. "
                    "Give short, practical advice. "
                    "Only use the prices I give you. Never guess plan names, "
                    "storage sizes or other prices, and do not add up totals. "
                    "Write every amount with this currency symbol: " + currency + "."
                )
                user_message = (
                    "Here are my subscriptions:\n" + summary +
                    "\n\nWhich ones should I question or cancel, "
                    "and how can I save money? "
                    "Give 3 to 5 short bullet points."
                )
                try:
                    client = Groq(api_key=api_key)
                    reply = client.chat.completions.create(
                        model=MODEL,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": user_message},
                        ],
                    )
                    tips = reply.choices[0].message.content
                    st.markdown(tips.replace("$", "\\$"))
                except Exception as error:
                    st.error(f"Something went wrong: {error}")
    else:
        st.write("No subscriptions found.")
