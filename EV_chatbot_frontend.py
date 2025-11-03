import streamlit as st
import random
import time


st.set_page_config(
    page_title="⚡ EV Chat & Dashboard",
    page_icon="🚗",
    layout="wide"
)


st.title("⚡ EVChat — Electric Vehicle Insights Dashboard")

st.markdown("""
Welcome to **EVChat**, your smart assistant for exploring Electric Vehicle (EV) data and insights.
You can chat about EV brands, performance, or pricing, and also see real-time stats and environmental impact!
""")


st.sidebar.header("🔍 Dashboard Options")
view_mode = st.sidebar.radio("Select View:", ["Chat", "Dashboard", "Environmental Impact"])


brands = ["Tesla", "BMW", "Audi", "BYD", "Tata", "Hyundai"]
avg_prices = {
    "Tesla": 60000, "BMW": 50000, "Audi": 55000,
    "BYD": 30000, "Tata": 25000, "Hyundai": 35000
}
avg_range = {
    "Tesla": 550, "BMW": 480, "Audi": 500,
    "BYD": 420, "Tata": 300, "Hyundai": 380
}
co2_savings_per_km = 0.12  # in kg CO₂ saved per km driven


if view_mode == "Chat":
    st.subheader("💬 EVChat Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:", placeholder="Ask something like 'Which EV has best range?'")

    if st.button("Send"):
        if user_input:
            st.session_state.chat_history.append(("You", user_input))

           
            if "range" in user_input.lower():
                best_brand = max(avg_range, key=avg_range.get)
                response = f"The EV with the best range is **{best_brand}** offering about **{avg_range[best_brand]} km** per charge."
            elif "cheap" in user_input.lower():
                cheapest = min(avg_prices, key=avg_prices.get)
                response = f"The cheapest EV brand currently is **{cheapest}**, priced around **${avg_prices[cheapest]:,}**."
            elif "brand" in user_input.lower():
                response = f"Popular EV brands include: {', '.join(brands)}."
            else:
                response = "I'm not sure, but I can tell you about EV brands, range, or prices!"

            st.session_state.chat_history.append(("EVChat", response))

    
    for sender, msg in st.session_state.chat_history:
        if sender == "You":
            st.markdown(f"🧍‍♀️ **{sender}:** {msg}")
        else:
            st.markdown(f"🤖 **{sender}:** {msg}")


elif view_mode == "Dashboard":
    st.subheader("📊 EV Brand Performance Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Average EV Price (USD)", f"${sum(avg_prices.values()) // len(avg_prices):,}")
        st.bar_chart(avg_prices)

    with col2:
        st.metric("Average EV Range (km)", f"{sum(avg_range.values()) // len(avg_range)} km")
        st.bar_chart(avg_range)

    st.markdown("✅ **Tip:** EV adoption is growing — average ranges are improving every year!")


elif view_mode == "Environmental Impact":
    st.subheader("🌱 Environmental Impact of EVs")

    st.markdown("""
    Compare **Electric Vehicles (EVs)** vs **Petrol Vehicles** in terms of carbon savings and energy efficiency.
    """)

    distance = st.slider("Select distance traveled (in km):", 10, 1000, 100)
    ev_efficiency = st.number_input("EV energy consumption (kWh per 100 km):", 10.0, 30.0, 15.0)
    fuel_efficiency = st.number_input("Petrol car fuel consumption (L per 100 km):", 3.0, 15.0, 7.0)

    ev_emission = distance * 0.05  # rough value
    petrol_emission = distance * 0.2
    co2_saved = petrol_emission - ev_emission

    st.write(f"🌍 By driving an EV for **{distance} km**, you save approximately **{co2_saved:.2f} kg of CO₂** compared to petrol vehicles.")

    st.progress(min(co2_saved / 200, 1.0))

    col1, col2 = st.columns(2)
    with col1:
        st.metric("EV CO₂ Emission", f"{ev_emission:.2f} kg")
    with col2:
        st.metric("Petrol CO₂ Emission", f"{petrol_emission:.2f} kg")

    st.markdown("""
    💡 **Insight:** EVs can reduce up to **70–80% CO₂ emissions** depending on the power source used for charging.
    """)


st.markdown("---")
st.caption("⚡ Built with Streamlit | Smart EVChat Dashboard")
