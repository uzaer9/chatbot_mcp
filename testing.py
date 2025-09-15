import streamlit as st
import pandas as pd
import json
import time

# --- Page Setup ---
st.set_page_config(
    page_title="Ronaldo Stats Bot",
    page_icon="🤖",
    layout="centered"
)

st.title("⚽ Cristiano Ronaldo Stats Bot")
st.caption("Ask me to 'show data' to see his performance from 2009-2012.")

# --- 1. PARSE AND COMBINE YOUR JSON DATA (from the original script) ---
json_data_0910 = { "league": "ESP-La Liga", "season": "0910", "stat_type": "standard", "filters": { "player": "Ronaldo", "team": "Real Madrid" }, "total_records": 1, "players": [ { "league,": "ESP-La Liga", "season,": "0910", "team,": "Real Madrid", "player,": "Cristiano Ronaldo", "nation,": "POR", "pos,": "FW,MF", "age,": 24, "born,": 1985, "Playing Time,MP": 29, "Playing Time,Starts": 28, "Playing Time,Min": 2461, "Playing Time,90s": 27.3, "Performance,Gls": 26, "Performance,Ast": 7, "Performance,G+A": 33, "Performance,G-PK": 22, "Performance,PK": 4, "Performance,PKatt": 5, "Performance,CrdY": 5, "Performance,CrdR": 2, "Per 90 Minutes,Gls": 0.95, "Per 90 Minutes,Ast": 0.26, "Per 90 Minutes,G+A": 1.21, "Per 90 Minutes,G-PK": 0.8, "Per 90 Minutes,G+A-PK": 1.06 } ] }
json_data_1011 = { "league": "ESP-La Liga", "season": "1011", "stat_type": "standard", "filters": { "player": "Ronaldo", "team": "Real Madrid" }, "total_records": 1, "players": [ { "league,": "ESP-La Liga", "season,": "1011", "team,": "Real Madrid", "player,": "Cristiano Ronaldo", "nation,": "POR", "pos,": "FW,MF", "age,": 25, "born,": 1985, "Playing Time,MP": 34, "Playing Time,Starts": 32, "Playing Time,Min": 2914, "Playing Time,90s": 32.4, "Performance,Gls": 40, "Performance,Ast": 9, "Performance,G+A": 49, "Performance,G-PK": 32, "Performance,PK": 8, "Performance,PKatt": 8, "Performance,CrdY": 2, "Performance,CrdR": 0, "Per 90 Minutes,Gls": 1.24, "Per 90 Minutes,Ast": 0.28, "Per 90 Minutes,G+A": 1.51, "Per 90 Minutes,G-PK": 0.99, "Per 90 Minutes,G+A-PK": 1.27 } ] }
json_data_1112 = { "league": "ESP-La Liga", "season": "1112", "stat_type": "standard", "filters": { "player": "Ronaldo", "team": "Real Madrid" }, "total_records": 1, "players": [ { "league,": "ESP-La Liga", "season,": "1112", "team,": "Real Madrid", "player,": "Cristiano Ronaldo", "nation,": "POR", "pos,": "FW,MF", "age,": 26, "born,": 1985, "Playing Time,MP": 38, "Playing Time,Starts": 37, "Playing Time,Min": 3350, "Playing Time,90s": 37.2, "Performance,Gls": 46, "Performance,Ast": 12, "Performance,G+A": 58, "Performance,G-PK": 34, "Performance,PK": 12, "Performance,PKatt": 13, "Performance,CrdY": 4, "Performance,CrdR": 0, "Per 90 Minutes,Gls": 1.24, "Per 90 Minutes,Ast": 0.32, "Per 90 Minutes,G+A": 1.56, "Per 90 Minutes,G-PK": 0.91, "Per 90 Minutes,G+A-PK": 1.24 } ] }

player_stats_list = [
    json_data_0910['players'][0],
    json_data_1011['players'][0],
    json_data_1112['players'][0]
]

# --- 2. CONVERT TO PANDAS DATAFRAME & CLEAN DATA ---
df = pd.DataFrame(player_stats_list)
df.columns = df.columns.str.replace(',', ' ').str.strip()
df = df.set_index('season')

# --- 3. CHATBOT INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! Ask me to 'show data' to see Ronaldo's stats."}
    ]

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # A bit of logic to handle re-displaying charts from history
        if "type" in message and message["type"] == "charts":
             st.markdown("Certainly! Here are Cristiano Ronaldo's performance stats:")
             st.subheader("Line Chart: Performance Trend")
             st.line_chart(df[['Performance Gls', 'Performance Ast', 'Performance G+A']])
             st.subheader("Bar Chart: Goals vs. Assists")
             st.bar_chart(df[['Performance Gls', 'Performance Ast']])
             st.subheader("Area Chart: Per 90 Minutes Statistics")
             st.area_chart(df[['Per 90 Minutes Gls', 'Per 90 Minutes Ast', 'Per 90 Minutes G+A']])
        else:
            st.markdown(message["content"])


# --- 4. MAIN CHAT LOGIC ---
if prompt := st.chat_input("What would you like to see?"):
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant's response logic
    with st.chat_message("assistant"):
        if "show data" in prompt.lower():
            with st.spinner("Fetching stats and building charts..."):
                time.sleep(1) # Simulate a bit of loading
                
                st.markdown("Certainly! Here are Cristiano Ronaldo's performance stats:")

                # --- Display all three charts from the original dashboard ---
                st.subheader("Line Chart: Performance Trend")
                df_performance = df[['Performance Gls', 'Performance Ast', 'Performance G+A']]
                st.line_chart(df_performance)

                st.subheader("Bar Chart: Goals vs. Assists")
                df_goals_assists = df[['Performance Gls', 'Performance Ast']]
                st.bar_chart(df_goals_assists)

                st.subheader("Area Chart: Per 90 Minutes Statistics")
                per_90_columns = ['Per 90 Minutes Gls', 'Per 90 Minutes Ast', 'Per 90 Minutes G+A']
                st.area_chart(df[per_90_columns])

                # Add a special message to session state to handle re-rendering the charts
                st.session_state.messages.append({"role": "assistant", "type": "charts", "content": "charts_displayed"})
        
        else:
            response = "Sorry, I can only respond to 'show data'. Please try that command."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

