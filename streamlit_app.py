from collections import defaultdict

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from app import get_forecast, get_weather

load_dotenv()

st.set_page_config(page_title="Weather App", page_icon="🌤️", layout="centered")
st.title("🌤️ Weather App")

city = st.text_input("Enter a city name", placeholder="e.g. London, Tokyo, New York")

if city:
    with st.spinner(f"Fetching weather for **{city}**..."):
        try:
            data = get_weather(city)

            if data.get("cod") != 200:
                st.error(f"City not found: **{city}**. Please check the spelling.")
            else:
                temp_k = data["main"]["temp"]
                temp_c = temp_k - 273.15
                temp_f = temp_c * 9 / 5 + 32
                humidity = data["main"]["humidity"]
                description = data["weather"][0]["description"].capitalize()
                country = data["sys"]["country"]

                st.subheader(f"{city.title()}, {country}")

                col1, col2, col3 = st.columns(3)
                col1.metric("Temperature", f"{temp_c:.1f} °C", f"{temp_f:.1f} °F")
                col2.metric("Humidity", f"{humidity}%")
                col3.metric("Condition", description)

                # --- 5-day forecast ---
                st.divider()
                st.subheader("📅 5-Day Forecast")

                forecast_data = get_forecast(city)
                if forecast_data.get("cod") != "200":
                    st.warning("Forecast data unavailable.")
                else:
                    # Group entries by calendar date, keep one per day (noon preferred)
                    daily = defaultdict(list)
                    for entry in forecast_data["list"]:
                        date = entry["dt_txt"].split(" ")[0]
                        daily[date].append(entry)

                    rows = []
                    for date, entries in list(daily.items())[:5]:
                        entry = next(
                            (e for e in entries if "12:00" in e["dt_txt"]),
                            entries[0],
                        )
                        temp_c = entry["main"]["temp"] - 273.15
                        temp_min_c = entry["main"]["temp_min"] - 273.15
                        temp_max_c = entry["main"]["temp_max"] - 273.15
                        rows.append({
                            "Date": date,
                            "Condition": entry["weather"][0]["description"].capitalize(),
                            "Temp (°C)": f"{temp_c:.1f}",
                            "Min (°C)": f"{temp_min_c:.1f}",
                            "Max (°C)": f"{temp_max_c:.1f}",
                            "Humidity (%)": entry["main"]["humidity"],
                            "Wind (m/s)": entry.get("wind", {}).get("speed", "—"),
                        })

                    st.dataframe(
                        pd.DataFrame(rows).set_index("Date"),
                        use_container_width=True,
                    )

        except Exception as e:
            st.error(f"Failed to fetch weather data: {e}")
