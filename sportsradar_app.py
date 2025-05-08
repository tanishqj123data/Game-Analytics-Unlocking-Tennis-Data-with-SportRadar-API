import streamlit as st
import mysql.connector
import pandas as pd

# Connect to MySQL
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456789",  # Replace with your password
        database="SportradarDB"
    )

# Query wrapper
def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Streamlit Layout
st.set_page_config(page_title="Sportradar Tennis Dashboard", layout="wide")
st.title("🎾 Sportradar Tennis Dashboard")

# Sidebar Menu
menu = st.sidebar.radio("Navigation", ["Home", "Leaderboards", "Players by Country"])

# 🏠 HOME DASHBOARD
if menu == "Home":
    st.subheader("📊 Overview")

    # Top Metrics
    col1, col2, col3 = st.columns(3)

    players = fetch_data("SELECT COUNT(*) AS total FROM Competitors")
    countries = fetch_data("SELECT COUNT(DISTINCT country) AS total FROM Competitors")
    venues = fetch_data("SELECT COUNT(*) AS total FROM Venues")

    col1.metric("Total Players", int(players['total'][0]))
    col2.metric("Countries Represented", int(countries['total'][0]))
    col3.metric("Venues", int(venues['total'][0]))

    # 🔎 Player Search Section
    st.subheader("🔎 Search for Players")

    # Fetch the list of all countries
    countries = fetch_data("SELECT DISTINCT country FROM Competitors WHERE country IS NOT NULL ORDER BY country ASC")
    country_list = ["All"] + countries["country"].tolist()

    # Add "All" option to the selectbox
    selected_country = st.selectbox("Select a Country", country_list)

    # Search Box for Player Name
    player_name = st.text_input("Search by Player Name (Partial or Full)")

    # Rank Range Slider
    rank_min, rank_max = st.slider("Select Rank Range", 1, 500, (1, 500))

    # Points Threshold Slider
    points_min, points_max = st.slider("Select Points Range", 0, 10000, (0, 10000))

    # Update the query based on the selection
    if selected_country == "All":
        query = f"""
            SELECT c.name AS player_name, c.country, c.abbreviation, r.rank, r.points
            FROM Competitor_Rankings r
            JOIN Competitors c ON r.competitor_id = c.competitor_id
            WHERE c.name LIKE '%{player_name}%'
            AND r.rank BETWEEN {rank_min} AND {rank_max}
            AND r.points BETWEEN {points_min} AND {points_max}
            ORDER BY r.rank ASC
        """
    else:
        query = f"""
            SELECT c.name AS player_name, c.country, c.abbreviation, r.rank, r.points
            FROM Competitor_Rankings r
            JOIN Competitors c ON r.competitor_id = c.competitor_id
            WHERE c.country = '{selected_country}'
            AND c.name LIKE '%{player_name}%'
            AND r.rank BETWEEN {rank_min} AND {rank_max}
            AND r.points BETWEEN {points_min} AND {points_max}
            ORDER BY r.rank ASC
        """

    # Fetch and display the data
    df = fetch_data(query)

    if selected_country == "All":
        st.write(f"Showing **{len(df)} players** from **All Countries**:")
    else:
        st.write(f"Showing **{len(df)} players** from **{selected_country}**:")
    
    st.dataframe(df)

# 🏆 LEADERBOARDS
elif menu == "Leaderboards":
    st.subheader("🏆 Top 20 Ranked Players")

    query = """
        SELECT c.name AS competitor_name, r.rank, r.points
        FROM Competitor_Rankings r
        JOIN Competitors c ON r.competitor_id = c.competitor_id
        ORDER BY r.rank ASC
        LIMIT 20
    """
    df = fetch_data(query)
    st.dataframe(df)

# 🌐 PLAYERS BY COUNTRY
elif menu == "Players by Country":
    st.subheader("🌐 Filter Players by Country")

    # Fetch the list of all countries
    countries = fetch_data("SELECT DISTINCT country FROM Competitors WHERE country IS NOT NULL ORDER BY country ASC")
    country_list = ["All"] + countries["country"].tolist()

    # Add "All" option to the selectbox
    selected_country = st.selectbox("Select a Country", country_list)

    # Update the main player query
    if selected_country == "All":
        query = """
            SELECT c.name AS player_name, c.country, c.abbreviation, r.rank, r.points, r.movement
            FROM Competitor_Rankings r
            JOIN Competitors c ON r.competitor_id = c.competitor_id
            ORDER BY r.rank ASC
        """
        # Summary for all players
        summary_query = """
            SELECT 
                COUNT(c.competitor_id) AS total_players,
                MIN(r.rank) AS top_rank,
                MAX(r.rank) AS lowest_rank,
                AVG(r.rank) AS avg_rank,
                AVG(r.points) AS avg_points,
                (SELECT c2.name 
                 FROM Competitor_Rankings r2
                 JOIN Competitors c2 ON r2.competitor_id = c2.competitor_id
                 WHERE r2.movement > 0
                 ORDER BY r2.movement DESC
                 LIMIT 1) AS top_mover,
                (SELECT r2.movement
                 FROM Competitor_Rankings r2
                 JOIN Competitors c2 ON r2.competitor_id = c2.competitor_id
                 WHERE r2.movement > 0
                 ORDER BY r2.movement DESC
                 LIMIT 1) AS highest_movement
            FROM Competitor_Rankings r
            JOIN Competitors c ON r.competitor_id = c.competitor_id;
        """
    else:
        query = f"""
            SELECT c.name AS player_name, c.country, c.abbreviation, r.rank, r.points, r.movement
            FROM Competitor_Rankings r
            JOIN Competitors c ON r.competitor_id = c.competitor_id
            WHERE c.country = '{selected_country}'
            ORDER BY r.rank ASC
        """
        # Summary for selected country
        summary_query = f"""
            SELECT 
                COUNT(c.competitor_id) AS total_players,
                MIN(r.rank) AS top_rank,
                MAX(r.rank) AS lowest_rank,
                AVG(r.rank) AS avg_rank,
                AVG(r.points) AS avg_points,
                (SELECT c2.name 
                 FROM Competitor_Rankings r2
                 JOIN Competitors c2 ON r2.competitor_id = c2.competitor_id
                 WHERE c2.country = '{selected_country}' AND r2.movement > 0
                 ORDER BY r2.movement DESC
                 LIMIT 1) AS top_mover,
                (SELECT r2.movement
                 FROM Competitor_Rankings r2
                 JOIN Competitors c2 ON r2.competitor_id = c2.competitor_id
                 WHERE c2.country = '{selected_country}' AND r2.movement > 0
                 ORDER BY r2.movement DESC
                 LIMIT 1) AS highest_movement
            FROM Competitor_Rankings r
            JOIN Competitors c ON r.competitor_id = c.competitor_id
            WHERE c.country = '{selected_country}';
        """

    # Fetch and display the player data
    df = fetch_data(query)

    # Fetch and display the summary data
    summary_df = fetch_data(summary_query)

    # Handle None values for the Most Improved Player
    top_mover = summary_df['top_mover'][0]
    highest_movement = summary_df['highest_movement'][0]

    # Use a fallback if no player has a positive movement
    if pd.isna(top_mover) or pd.isna(highest_movement):
        col6_metric = ("No Data", "N/A")
    else:
        col6_metric = (top_mover, int(highest_movement))

    # Display the summary metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Players", int(summary_df['total_players'][0]))
    col2.metric("Top Rank", int(summary_df['top_rank'][0]))
    col3.metric("Lowest Rank", int(summary_df['lowest_rank'][0]))
    col4.metric("Average Rank", round(summary_df['avg_rank'][0], 2))
    col5.metric("Average Points", round(summary_df['avg_points'][0], 2))
    col6.metric("Most Improved", col6_metric[0], delta=col6_metric[1])

    # Display the player data
    if selected_country == "All":
        st.write(f"Showing **{len(df)} players** from **All Countries**:")
    else:
        st.write(f"Showing **{len(df)} players** from **{selected_country}**:")
    
    st.dataframe(df)
