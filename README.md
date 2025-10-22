# Udemy Course Analysis & Recommendation System

This is an end-to-end data science project that analyzes, cleans, and engineers data from a Udemy courses dataset. The data is migrated to a cloud-based **Supabase (PostgreSQL)** database, and the final insights are served through a live, multi-page **Streamlit** dashboard.

The final app provides course recommendations, deep-dive analytics, and pricing optimization strategies.

## 🚀 Live Interactive Dashboard

The fully interactive dashboard is live and accessible to everyone.

**➡️ [Click here to use the live app](https://udemy-courses-recommendation-system.streamlit.app/)**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://udemy-courses-recommendation-system.streamlit.app/)

*(Remember to replace the URL above with your actual Streamlit app URL)*

## Key Features

* **🚀 Live Interactive Dashboard:** A multi-page Streamlit application for exploring all project insights.
* **💡 Content-Based Recommendation Engine:** Uses `TfidfVectorizer` and `Cosine Similarity` on course titles to recommend similar courses.
* **☁️ Cloud Database Backend:** The entire project is powered by a **Supabase (PostgreSQL)** database, with the app connecting securely via Streamlit's secrets and the robust **Session Pooler**.
* **📊 Advanced SQL Analytics:** The database backend features **10 pre-built SQL views** (e.g., `vw_market_gaps`, `vw_top_courses`, `vw_subject_performance`) to pre-aggregate complex data for fast dashboard loading.
* **💰 Dynamic Price Optimizer:** Provides pricing strategies (Conservative, Balanced, Premium) by analyzing the prices of similar, high-quality courses.
* **🐍 End-to-End Python Pipeline:** Includes scripts for data exploration (`Data Exploration.ipynb`), data cleaning and migration (`run_data_import.py`), and the final application (`recommendation_system.py`).

## 💻 Tech Stack

* **Frontend / Dashboard:** Streamlit
* **Backend Database:** Supabase (PostgreSQL)
* **Data Science & ML:** Python, Pandas, Scikit-learn
* **Database Connection:** `psycopg2-binary`, `SQLAlchemy`
* **Data Exploration:** Jupyter Notebook, SQL

## 🏗️ Project Architecture & Workflow

This project is built as a complete data pipeline, with each file serving a specific purpose.

1.  **`Data Exploration.ipynb`**
    * The initial scratchpad.
    * Loads the raw `Udemy Courses.csv`.
    * Performs initial exploratory data analysis (EDA), data cleaning, and feature engineering (e.g., `popularity_score`, `price_category`).

2.  **`SQL Queries.sql`**
    * The complete architectural blueprint for the PostgreSQL database.
    * Creates the main `udemy_courses` table.
    * Establishes all **10 analytical VIEWs** that power the dashboard's analytics pages.

3.  **`run_data_import.py`**
    * The ETL (Extract, Transform, Load) script for the project.
    * It automatically reads the `secrets.toml` file to connect to the Supabase database.
    * Performs the final data cleaning from the notebook, including dropping duplicates.
    * **Truncates** (empties) the existing table to avoid errors.
    * Uses `SQLAlchemy` to efficiently load the clean 3,672-row DataFrame into the Supabase database.

4.  **`recommendation_system.py`**
    * The final, live Streamlit application.
    * Connects securely to the Supabase **Session Pooler** using `st.secrets`.
    * Loads data from the main table and the 10 SQL views.
    * Serves all interactive charts, dataframes, and the recommendation engine.

## ⚙️ How to Run This Project Locally

To clone and run this project on your own machine, follow these steps:

1.  **Clone the Repository**
    ```sh
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Set Up a Supabase Database**
    * Create a free project on [Supabase](https://supabase.com/).
    * Go to the **SQL Editor** and run the entire `SQL Queries.sql` script to create your tables and views.
    * Go to **Project Settings** > **Database** > **Connection string** and get your "Session Pooler" credentials.

3.  **Create Your Local Secrets File**
    * Create a file named `secrets.toml` in the root of the project.
    * Add your "Session Pooler" credentials to it. **This file must not be committed to GitHub.**

    ```toml
    # secrets.toml
    DB_HOST = "aws-0-us-west-2.pooler.supabase.com"
    DB_USER = "postgres.your-project-ref"
    DB_PORT = "5432"
    DB_NAME = "postgres"
    DB_PASSWORD = "Your-Database-Password"
    ```

4.  **Install Dependencies**
    * Ensure you have Python 3.8+ installed.
    * Install all required libraries from `requirements.txt`. (Ensure it uses `psycopg2-binary`, not `pyodbc`).
    ```sh
    pip install -r requirements.txt
    ```

5.  **Run the Data Import**
    * This script will read your `secrets.toml` and upload the data from `Udemy Courses.csv`.
    ```sh
    python run_data_import.py
    ```

6.  **Run the Streamlit App**
    * The app will automatically read your `secrets.toml` file to connect.
    ```sh
    streamlit run recommendation_system.py
    ```

---

## 🖼️ App Screenshots

*Overview Page*
<img width="1920" height="957" alt="{89BA96A6-BCA0-49E1-996D-A4564B1817EC}" src="https://github.com/user-attachments/assets/0574d71f-0b3e-40cb-adef-392052f825f3" />
<img width="1920" height="948" alt="{45342B81-ACD1-4E4A-854F-CC28A40D29A3}" src="https://github.com/user-attachments/assets/42f0a072-57df-42b3-879b-46657a665610" />

*Recommendation Page*
<img width="1920" height="931" alt="{78066D9F-A63B-4826-9AAA-1E8E81FC0DB4}" src="https://github.com/user-attachments/assets/93d21216-f801-47bd-8c66-17680eb16298" />
<img width="1920" height="907" alt="{A0B4F8B5-D7E0-4C12-8D13-42714484FC87}" src="https://github.com/user-attachments/assets/bd477296-b9f1-4927-b0f1-e90cc40fc772" />

*Course Explorer Page*
<img width="1920" height="954" alt="{766E29BD-6FB8-4F89-BFB8-CB5F900DA579}" src="https://github.com/user-attachments/assets/c1e7a9b4-0418-42f9-8aa8-a83a32dd97b9" />

*Analytics Page*
<img width="1920" height="943" alt="{5443AB2B-2E32-4063-AE03-0C8F1AEB8039}" src="https://github.com/user-attachments/assets/e105c5d3-cd62-4cae-b9a4-c9783ba56b79" />
<img width="1858" height="896" alt="{EB3C120D-E611-47A5-9808-0A3B3F38C63B}" src="https://github.com/user-attachments/assets/05270f4c-e396-473b-a051-954a45318852" />
<img width="1891" height="994" alt="{A0BE983F-225E-4789-A540-ED2928BF5FCA}" src="https://github.com/user-attachments/assets/866ec7e8-0d76-4d76-8372-258c9d48e694" />

*Price Optimizer Page*
<img width="1920" height="942" alt="{717C3A5A-CD13-4A69-93FE-5FE576E5A2E2}" src="https://github.com/user-attachments/assets/076ba32f-b06c-49c8-a5f1-7d926256562f" />
<img width="1920" height="908" alt="{DD9FA503-89C7-4B46-81C8-E2236CCAF5CE}" src="https://github.com/user-attachments/assets/48df3032-2309-45b6-8fcd-2d4c6e1c51e1" />
