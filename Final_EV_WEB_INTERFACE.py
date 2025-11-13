import streamlit as st
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import google.generativeai as genai

GEMINI_API_KEY = " " # I USED MY API KEY (SECRET KEY)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash')

# Load CSV
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

st.title("⚡EVTalk – Your Electric Vehicle Chat Assistant")
uploaded_file = st.file_uploader("Upload Electric Vehicles CSV", type=['csv'])
if uploaded_file:
    df = load_data(uploaded_file)
    st.write("Preview of Dataset:")
    st.dataframe(df.head())

    #  Training of the data
    df = df.dropna(subset=["brand", "battery_capacity_kWh", "range_km"])
    brand_encoder = LabelEncoder()
    df["brand_encoded"] = brand_encoder.fit_transform(df["brand"])
    X = df[["brand_encoded"]]
    y_battery = df["battery_capacity_kWh"]
    y_range = df["range_km"]
    X_train, X_test, y_bat_train, y_bat_test = train_test_split(X, y_battery, test_size=0.2, random_state=42)
    X_train2, X_test2, y_rng_train, y_rng_test = train_test_split(X, y_range, test_size=0.2, random_state=42)
    battery_model = LinearRegression()
    battery_model.fit(X_train, y_bat_train)
    range_model = LinearRegression()
    range_model.fit(X_train2, y_rng_train)

    st.session_state.setdefault("messages", [])
    new_user_msg = st.text_input("Ask a question about EVs!", "")
    
    with st.sidebar:
        st.header("EV Brand and Model Filter")
        brand_list = sorted(df["brand"].unique())
        brand_choice = st.selectbox("Select a Brand", ["All"] + brand_list)

        if brand_choice != "All":
            model_list = sorted(df[df["brand"] == brand_choice]["model"].unique())
            model_choice = st.selectbox("Select a Model", ["All"] + model_list)
        else:
            model_choice = "All"

        filtered = df.copy()
        if brand_choice != "All":
            filtered = filtered[filtered["brand"] == brand_choice]
        if model_choice != "All":
            filtered = filtered[filtered["model"] == model_choice]

        if not filtered.empty:
            st.subheader("Matching EVs")
            st.dataframe(filtered)
            st.subheader("Source URLs")
            for url in filtered["source_url"].unique():
                st.write(url)
        else:
            st.write("No vehicles match the selected criteria.")

        
    # Chatbot answer logic
    def answer(query):
        q = query.lower()
        
        env_keywords = ['environment', 'co2', 'carbon', 'pollution', 'emission', 'sustainability', 'climate', 'global warming','sources']
        if any(word in q for word in env_keywords):
            # Use Gemini for these questions!
#             model = genai.GenerativeModel('gemini-pro')
            chat = model.start_chat()
            prompt = (
                        f"Answer as an EV specialist: {query} "
                        "Give a concise, clear answer suitable for a chatbot. "
                        "Limit your response to 7-8 sentences or less than 150 words."
                    )            
            gemini_reply = chat.send_message(prompt)
            return gemini_reply.text
        
        
        if "give information about" in q:
            for brand in df["brand"].unique():
                if brand.lower() in q:
                    # Filter rows for the brand
                    brand_df = df[df["brand"].str.lower() == brand.lower()]
                    st.write(f"Showing all data for **{brand}**:")
                    st.dataframe(brand_df)
                    return ""  
            return "Brand not found."
        
        elif "list all brands" in q or "show all brands" in q or "list all the brands"in q or "show all the brands" in q:
            brands = sorted(df["brand"].unique())
            return "All 🚗 brands in the dataset:\n" + ", ".join(brands)
        elif "highest" in q and "battery" in q:
            idx = df["battery_capacity_kWh"].idxmax()
            row = df.loc[idx]
            return f"{row['brand']} {row['model']} has the highest battery: {row['battery_capacity_kWh']} kWh."
        elif "lowest" in q and "battery" in q:
            idx = df["battery_capacity_kWh"].idxmin()
            row = df.loc[idx]
            return f"{row['brand']} {row['model']} has the lowest battery: {row['battery_capacity_kWh']} kWh."
        elif "highest" in q and "range" in q:
            idx = df["range_km"].idxmax()
            row = df.loc[idx]
            return f"{row['brand']} {row['model']} has the highest range: {row['range_km']} km."
        elif "lowest" in q and "range" in q:
            idx = df["range_km"].idxmin()
            row = df.loc[idx]
            return f"{row['brand']} {row['model']} has the lowest range: {row['range_km']} km."
        elif "models" in q and "brand" in q:
            for brand in df["brand"].unique():
                if brand.lower() in q:
                    mods = df[df["brand"] == brand]["model"].unique()
                    return f"Models for {brand}: {', '.join(mods)}"
            return "Please specify a brand."
        elif "best" in q or "optimal" in q:
            brand = None
            for b in df["brand"].unique():
                if b.lower() in q:
                    brand = b
                    break
            if brand:
                best_idx = df[df["brand"] == brand]["range_km"].idxmax()
                best_row = df.loc[best_idx]
                return f"Best model in {brand} by range: {best_row['model']} ({best_row['range_km']} km)."
            else:
                best_idx = df["range_km"].idxmax()
                best_row = df.loc[best_idx]
                return f"Best overall: {best_row['brand']} {best_row['model']} with range {best_row['range_km']} km."
        elif "predict" in q and "battery" in q:
            for brand in df["brand"].unique():
                if brand.lower() in q:
                    bcode = brand_encoder.transform([brand])[0]
                    battery_est = battery_model.predict([[bcode]])[0]
                    range_est = range_model.predict([[bcode]])[0]
                    return f"Prediction for {brand}: Battery ≈ {battery_est:.1f} kWh, Range ≈ {range_est:.0f} km"
            return "Specify a brand to predict."
        elif "models" in q and "in" in q:
        # Extract the brand name from the question
            tokens = q.split("in")
            if len(tokens) > 1:
                brand_asked = tokens[1].strip().capitalize()
                brands = [b for b in df["brand"].unique() if brand_asked.lower() in b.lower()]
                if brands:
                    all_models = []
                    for b in brands:
                        mods = df[df["brand"].str.lower() == b.lower()]["model"].unique()
                        all_models.extend([f"{b} {m}" for m in mods])
                    return "Models in 🚗 " + ", ".join(brands) + ":\n" + "\n".join(all_models)
                else:
                    return f"No models found for brand '{brand_asked}'."
        else:
            return "Ask about battery, range, best, worst, or models! Specify brand when possible."

    # Add user message to chat history
    if new_user_msg:
        st.session_state.messages.append(("😊 USER", new_user_msg))
        print()
        bot_reply = answer(new_user_msg)
        print()
        st.session_state.messages.append(("👾  BOT", bot_reply))
        print()
        print()

    # Show chat history
    # Split the messages into pairs
    pairs = [(st.session_state.messages[i], st.session_state.messages[i+1])
             for i in range(0, len(st.session_state.messages), 2)]

    # Reverse the pairs
    for user_msg, bot_msg in reversed(pairs):
        st.write(f"**{user_msg[0]}:** {user_msg[1]}")
        st.write(f"**{bot_msg[0]}:** {bot_msg[1]}")


    # Chat backup
    chat_lines = []
    for user_msg, bot_msg in reversed(pairs):
        chat_lines.append(f"{user_msg[0]}:{user_msg[1]}")
        chat_lines.append(f"{bot_msg[0]}:{bot_msg[1]}")
    st.download_button("Export Chat History", 
        data="\n".join(chat_lines),
        file_name="ev_chat_backup.txt")

else:
    st.info("Upload your EV dataset to begin chatting.")

