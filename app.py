import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv("data/destinations.csv")

# Scoring functions
def temperature_score(temp, preferred_min, preferred_max):
    if preferred_min <= temp <= preferred_max:
        return 100
    distance = min(abs(temp - preferred_min), abs(temp - preferred_max))
    return max(0, 100 - distance * 10)

def budget_score(price, max_budget):
    if price <= max_budget:
        return 100
    return max(0, 100 - (price - max_budget))

def safety_score(dest_safety, min_safety):
    if dest_safety >= min_safety:
        return 100
    return max(0, 100 - (min_safety - dest_safety) * 5)

def duration_score(duration, max_duration):
    if duration <= max_duration:
        return 100
    return max(0, 100 - (duration - max_duration) * 30)

def type_score(dest_type, preferred_type):
    return 100 if dest_type == preferred_type else 40

# UI
st.title("✈️ FitMyTrip")
st.subheader("Find your ideal travel destination in Europe")

# Sidebar
st.sidebar.header("Your Preferences")

min_temp = st.sidebar.slider("Min temperature", 0, 35, 20)
max_temp = st.sidebar.slider("Max temperature", 0, 40, 25)
budget = st.sidebar.slider("Max budget (€)", 50, 400, 200)
safety = st.sidebar.slider("Min safety", 0, 100, 75)
duration = st.sidebar.slider("Max travel duration (h)", 0.5, 5.0, 3.0)

dest_type = st.sidebar.selectbox(
    "Destination type",
    ["Beach", "City", "Mountains", "Nature"]
)

# Weights
st.sidebar.header("Importance")

w_temp = st.sidebar.slider("Temperature importance", 0, 10, 7)
w_budget = st.sidebar.slider("Budget importance", 0, 10, 8)
w_safety = st.sidebar.slider("Safety importance", 0, 10, 6)
w_duration = st.sidebar.slider("Duration importance", 0, 10, 6)
w_type = st.sidebar.slider("Type importance", 0, 10, 9)

# Calculate scores
df["temp_score"] = df["avg_temperature"].apply(lambda x: temperature_score(x, min_temp, max_temp))
df["budget_score"] = df["flight_price"].apply(lambda x: budget_score(x, budget))
df["safety_match"] = df["safety_score"].apply(lambda x: safety_score(x, safety))
df["duration_score"] = df["travel_duration"].apply(lambda x: duration_score(x, duration))
df["type_score"] = df["destination_type"].apply(lambda x: type_score(x, dest_type))

total_weight = w_temp + w_budget + w_safety + w_duration + w_type

df["final_score"] = (
    df["temp_score"] * w_temp +
    df["budget_score"] * w_budget +
    df["safety_match"] * w_safety +
    df["duration_score"] * w_duration +
    df["type_score"] * w_type
) / total_weight

df = df.sort_values(by="final_score", ascending=False)

# Top 3
st.header("🏆 Top 3 Destinations")

top3 = df.head(3)
cols = st.columns(3)

for i, row in enumerate(top3.itertuples()):
    with cols[i]:
        st.metric(f"{i+1}. {row.city}", f"{row.final_score:.1f}/100")
        st.write(f"🌡 {row.avg_temperature}°C")
        st.write(f"💰 €{row.flight_price}")
        st.write(f"🛡 {row.safety_score}")
        st.write(f"⏱ {row.travel_duration}h")
        st.write(f"🏖 {row.destination_type}")

# Chart
st.header("📊 Top Destinations")

fig = px.bar(df.head(10), x="city", y="final_score", color="destination_type")
st.plotly_chart(fig)

# Details
st.header("🔍 Why this destination?")

selected_city = st.selectbox("Select destination", df["city"])
selected = df[df["city"] == selected_city].iloc[0]

details = pd.DataFrame({
    "Criteria": ["Temp", "Budget", "Safety", "Duration", "Type"],
    "Score": [
        selected["temp_score"],
        selected["budget_score"],
        selected["safety_match"],
        selected["duration_score"],
        selected["type_score"]
    ]
})

fig2 = px.bar(details, x="Criteria", y="Score", range_y=[0, 100])
st.plotly_chart(fig2)

# Table
st.dataframe(df)


