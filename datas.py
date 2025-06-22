import psycopg2
import pandas as pd
from datetime import datetime
import streamlit as st

# connect to postgres 
connection = psycopg2.connect(
    host="localhost",
    user="postgres",        # Use your PostgreSQL username (commonly "postgres")
    password="thennarasu",    # Replace with your PostgreSQL password
    database="secure"      # Use the correct database name
)

cursor = connection.cursor()
print("Connected to PostgreSQL!")
# Check if the table already has data
cursor.execute('SELECT COUNT(*) FROM police')
result = cursor.fetchone()

# Insert the new data
if result[0] == 0:
    df = pd.read_csv(r"C:\Users\Thennarasu\Documents\dataset\traffic_stops - traffic_stops_with_vehicle_number.csv")
    df['search_type'].fillna(df['search_type'].mode()[0], inplace=True) #To fill missing values
    df = df.drop (['driver_age_raw','violation_raw'], axis=1)
    data = df.values.tolist()
    new_data = []
    for row in data:
        stop_date = datetime.strptime(row[0], "%Y-%m-%d").date()
        stop_time = datetime.strptime(row[1], "%H:%M:%S").strftime(("%H:%M:%S"))
 
        new_row = (
            stop_date,
            stop_time,
            str(row[2]),
            str(row[3]),
            int(row[4]),
            str(row[5]),
            str(row[6]),
            bool(row[7]),
            str(row[8]),
            str(row[9]),
            bool(row[10]),
            str(row[11]),
            bool(row[12]),
            str(row[13]),
        )
        new_data.append(new_row)
    query = "INSERT INTO Police VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(query, new_data)
    connection.commit()

# Theme selection
theme = st.selectbox("Choose Theme", ["Dark", "Light"])

# Inject CSS based on selected theme
if theme == "Dark":
    st.markdown("""
        <style>
            html, body, [data-testid="stApp"] {
                background-color: #0e1117;
                color: #FAFAFA;
            }
            h1 {
                color: #58a6ff;
            }
            h2, h3, h4 {
                color: #c9d1d9;
            }
            div[data-testid="metric-container"] {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 10px;
                padding: 10px;
                color: #FAFAFA;
            }
            label, input, textarea, select, div[data-baseweb="select"] {
                color: #FAFAFA !important;
                background-color: #161b22 !important;
            }
            .stButton>button {
                background-color: #238636;
                color: #ffffff;
                border-radius: 8px;
            }
            .stDataFrame, .stTable {
                background-color: #161b22;
                color: #FAFAFA;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            html, body, [data-testid="stApp"] {
                background-color: #ffffff;
                color: #000000;
            }
            h1 {
                color: #1a1a1a;
            }
            h2, h3, h4 {
                color: #333333;
            }
            div[data-testid="metric-container"] {
                background-color: #f0f2f6;
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
            label, input, textarea, select, div[data-baseweb="select"] {
                color: #000000 !important;
                background-color: #ffffff !important;
            }
            .stButton>button {
                background-color: #0066cc;
                color: #ffffff;
                border-radius: 8px;
            }
            .stDataFrame, .stTable {
                background-color: #ffffff;
                color: #000000;
            }
        </style>
    """, unsafe_allow_html=True)

# Dashboard Title
st.title("SecureCheck Dashboard")
# Set up Streamlit app
st.set_page_config(page_title="police_check", layout="wide")
query = "SELECT * FROM Police"
df = pd.read_sql(query, connection)

#Filters
st.header("Filters")
min_date = df['stop_date'].min()
max_date = df['stop_date'].max()
start_date = st.date_input("From", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.date_input("To", min_value=min_date, max_value=max_date, value=max_date)
df['stop_date'] = pd.to_datetime(df['stop_date'])
df = df[(df['stop_date'] >= pd.to_datetime(start_date)) & (df['stop_date'] <= pd.to_datetime(end_date))]
gender = st.selectbox("Filter by Driver Gender", options=['All'] + df['driver_gender'].dropna().unique().tolist())
violation = st.selectbox("Filter by Violation Type", options=['All'] + df['violation'].dropna().unique().tolist())
if gender != 'All':
    df = df[df['driver_gender'] == gender]
if violation != 'All':
    df = df[df['violation'] == violation]

# Key Metrics 
st.header("Key Metrics")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Arrests", int(df['is_arrested'].sum()))
with col2:
    st.metric("Drug-Related Stops", int(df['drugs_related_stop'].sum()))

# Display Filtered Data 
st.header("Police Post Log Data")
st.dataframe(df)

#  Violation Counts Table 
violation_counts = df['violation'].value_counts().reset_index()
violation_counts.columns = ['Violation Type', 'Count']
st.subheader("Most Common Violations")
st.dataframe(violation_counts)

#Display Medium Level Queries
st.header("Advanced Insights")
st.markdown("### SQL QUERIES (Medium level)")
query_categories = {
    "Vehicle-Based": {
        "What are the top 10 vehicles involved in drug-related stops":
            "SELECT vehicle_number, COUNT(*) AS count FROM Police WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY count DESC LIMIT 10",
        "Which vehicles were most frequently searched?":
            "SELECT vehicle_number, COUNT(*) AS count FROM Police WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY count DESC LIMIT 10"
    },
    "Demographic-Based": {
        "Which driver age group had the highest arrest rate?":
            "SELECT driver_age, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS arrest_rate FROM Police GROUP BY driver_age ORDER BY arrest_rate DESC LIMIT 10",
        "What is the gender distribution of drivers stopped in each country?":
            "SELECT country_name, driver_gender, COUNT(*) AS count FROM Police GROUP BY country_name, driver_gender ORDER BY country_name",
        "Which race and gender combination has the highest search rate?":
            "SELECT driver_race, driver_gender, COUNT(*) AS total, SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS searches, ROUND(SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS search_rate FROM Police GROUP BY driver_race, driver_gender ORDER BY search_rate DESC LIMIT 10"
    },
    "Time & Duration Based": {
        "What time of day sees the most traffic stops?":
            "SELECT EXTRACT(HOUR FROM stop_time) AS hour_of_day, COUNT(*) AS stop_count FROM Police GROUP BY hour_of_day ORDER BY stop_count DESC",
        "What is the average stop duration for different violations?":
            "SELECT violation, ROUND(AVG(CASE WHEN stop_duration ~ '^[0-9]+' THEN (SUBSTRING(stop_duration FROM '^[0-9]+')::INTEGER) ELSE NULL END), 2) AS avg_duration FROM Police GROUP BY violation ORDER BY avg_duration DESC",
        "Are stops during the night more likely to lead to arrests?":
            "SELECT CASE WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 20 AND 23 OR EXTRACT(HOUR FROM stop_time) BETWEEN 0 AND 5 THEN 'Night' ELSE 'Day' END AS time_period, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS arrest_rate FROM Police GROUP BY time_period"
    },
    "Violation-Based": {
        "Which violations are most associated with searches or arrests?":
            "SELECT violation, SUM(CASE WHEN search_conducted THEN 1 ELSE 0 END) AS total_searches, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS total_arrests FROM Police GROUP BY violation ORDER BY total_searches DESC, total_arrests DESC LIMIT 10",
        "Which violations are most common among younger drivers (<25)?":
            "SELECT violation, COUNT(*) AS count FROM Police WHERE driver_age BETWEEN 16 AND 25 GROUP BY violation ORDER BY count DESC LIMIT 10",
        "Is there a violation that rarely results in search or arrest?":
            "SELECT violation, COUNT(*) AS count FROM Police WHERE search_conducted = FALSE OR is_arrested = FALSE GROUP BY violation ORDER BY count DESC"
    },
    "Location-Based": {
        "Which countries report the highest rate of drug-related stops?":
            "SELECT country_name, COUNT(*) AS total_stops, SUM(CASE WHEN drugs_related_stop THEN 1 ELSE 0 END) AS drug_related, ROUND(SUM(CASE WHEN drugs_related_stop THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS drug_rate FROM Police GROUP BY country_name ORDER BY drug_rate DESC LIMIT 10",
        "What is the arrest rate by country and violation?":
            "SELECT country_name, violation, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END) AS arrests, ROUND(SUM(CASE WHEN is_arrested THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 2) AS arrest_rate FROM Police GROUP BY country_name, violation ORDER BY arrest_rate DESC LIMIT 10",
        "Which country has the most stops with search conducted?":
            "SELECT country_name, COUNT(*) AS total_searches FROM Police WHERE search_conducted = TRUE GROUP BY country_name ORDER BY total_searches DESC LIMIT 5"
    }
}

selected_category = st.selectbox("Select a category", list(query_categories.keys()))
selected_question = st.selectbox("Select a query", list(query_categories[selected_category].keys()))
if st.button("Run Medium Level Query"):
    query = query_categories[selected_category][selected_question]
    result = pd.read_sql(query, connection)
    if not result.empty:
        st.dataframe(result)
    else:
        st.warning("No results found for the selected query.")

# Display Complex Queries
st.markdown("### SQL QUERIES (Complex Level)")
complex_queries = {
    "Yearly Breakdown of Stops and Arrests by Country":
        """
        SELECT country_name,
               EXTRACT(YEAR FROM stop_date) AS year,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests
        FROM police
        GROUP BY country_name, year
        ORDER BY country_name, year;
        """,

    "Driver Violation Trends Based on Age and Race":
        """
        SELECT driver_age,
               driver_race,
               violation,
               COUNT(*) AS count
        FROM police
        GROUP BY driver_age, driver_race, violation
        ORDER BY count DESC;
        """,

    "Time Period Analysis of Stops":
        """
        SELECT EXTRACT(YEAR FROM stop_date) AS year,
               EXTRACT(MONTH FROM stop_date) AS month,
               COUNT(*) AS stop_count
        FROM police
        GROUP BY year, month
        ORDER BY year, month;
        """,

    "Number of Stops by Year, Month, Hour of the Day":
        """
        SELECT EXTRACT(YEAR FROM stop_date) AS year,
               EXTRACT(MONTH FROM stop_date) AS month,
               EXTRACT(HOUR FROM stop_time) AS hour,
               COUNT(*) AS stop_count
        FROM police
        GROUP BY year, month, hour
        ORDER BY year, month, hour;
        """,

    "Violations with High Search and Arrest Rates":
        """
        SELECT violation,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches,
               SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests
        FROM police
        GROUP BY violation
        ORDER BY total_searches DESC, total_arrests DESC;
        """,

    "Driver Demographics by Country":
        """
        SELECT country_name,
               driver_gender,
               driver_race,
               driver_age,
               COUNT(*) AS total
        FROM police
        GROUP BY country_name, driver_gender, driver_race, driver_age
        ORDER BY country_name, total DESC;
        """,

    "Top 5 Violations with Highest Arrest Rates":
        """
        SELECT violation,
               COUNT(*) AS total_stops,
               SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
               ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)::NUMERIC * 100 / COUNT(*), 2) AS arrest_rate
        FROM police
        GROUP BY violation
        HAVING COUNT(*) > 50
        ORDER BY arrest_rate DESC
        LIMIT 5;
        """
}
selected_complex_query = st.selectbox("Select a complex query", list(complex_queries.keys()))
if st.button("Run Complex Query"):
    query = complex_queries[selected_complex_query]
    result = pd.read_sql(query, connection)
    if not result.empty:
        st.dataframe(result)
    else:
        st.warning("No results found for the selected query.")
       
# Add New Police Log & Predict Outcome and Violation
st.header("Add New Police Log & Predict Outcome and Violation")
with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    county_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", df['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()
    submitted = st.form_submit_button("Predict Stop Outcome & Violation")
    if submitted:
        filtered_data = df[
            (df['driver_gender'] == driver_gender) &
            (df['driver_age'] == driver_age) &
            (df['search_conducted'] == int(search_conducted)) &
            (df['stop_duration'] == stop_duration) &
            (df['drugs_related_stop'] == int(drugs_related_stop))
        ]
        if not filtered_data.empty:
            predicted_outcome = filtered_data["stop_outcome"].mode()[0]
            predicted_violation = filtered_data["violation"].mode()[0]
        else:
            predicted_outcome = "warning"
            predicted_violation = "speeding"
        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "Drug-related" if int(drugs_related_stop) else "Not drug-related"
        st.markdown(f"""
            🛑🚗 A {driver_age}-year-old {driver_gender} driver was stopped for {predicted_violation} at {stop_time.strftime('%I:%M %p')}. {search_text} and they recieved a {predicted_outcome}. The stop lasted {stop_duration} minutes and was {drug_text}.
        """)

