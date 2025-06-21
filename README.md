
# 🚨 SecureCheck: Police Traffic Stop Analysis Dashboard

SecureCheck is a powerful, interactive Streamlit dashboard for analyzing police traffic stop data stored in PostgreSQL. It enables users to visualize traffic stop trends, filter data, run medium and complex SQL queries, and even simulate predictions for new police logs.

---

## 🧰 Features

- 📤 Automatically imports traffic stop data from CSV into PostgreSQL
- 🌓 Theme toggle between Light and Dark mode using custom CSS
- 🗓️ Filter traffic stop data by date range, driver gender, and violation type
- 📊 Key metrics including:
  - Total number of arrests
  - Total number of drug-related stops
- 📈 Medium-level and complex SQL queries categorized by:
  - Vehicle-related analysis
  - Demographic trends
  - Violation-based insights
  - Time-based stop analysis
  - Country-wise and location-based patterns
- 🤖 Predict violation type and outcome based on form data using filtered mode logic
- 📄 Display full and filtered dataset tables

---

## 📦 Technologies Used

- **Python 3**
- **Streamlit**
- **PostgreSQL**
- **Pandas**
- **psycopg2**

---

## 📁 Project Structure

```bash
securecheck/
├── app.py                 # Main Streamlit dashboard
├── traffic_stops.csv      # Input dataset (example path to CSV)
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

---

### 4. Set up PostgreSQL

- Create a database named `secure`
- Create a table named `police` with appropriate schema
- Update your PostgreSQL credentials inside `app.py`:
  ```python
  psycopg2.connect(
      host="localhost",
      user="postgres",     ## user means based on sql
      password="your_password",
      database="secure"
  )
  ```

### 5. Run the Streamlit App

```bash
streamlit run app.py
```

---

## 🧪 SQL Insights Categories

- **Vehicle-Based**: Most searched vehicles, drug-related vehicles
- **Demographic-Based**: Arrests by age group, gender distribution
- **Time & Duration**: Stops by hour, average durations
- **Violation-Based**: Frequent violations by age, type
- **Location-Based**: Top countries by search, arrest, drug-related stop rate

---

## ✨ Prediction Feature

Submit a new traffic stop log through the form to receive a predicted:
- **Violation type**
- **Stop outcome (e.g.  speeding, warning)**

---

## 📜 License

This project is open-source and free to use.

---

Built with ❤️ by Vilarasu
