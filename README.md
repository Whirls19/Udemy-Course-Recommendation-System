# Udemy Course Analysis & Recommendation System

This project analyzes a dataset of Udemy courses to uncover insights and provide course recommendations. It features a complete data pipeline: from initial data exploration and feature engineering, through integration into a SQL Server database, to a final interactive web application built with Streamlit.

## 🚀 Features

* **Interactive Streamlit Dashboard:** A user-friendly web interface to explore course data and get recommendations.
* **Content-Based Recommendation Engine:** Recommends similar courses using **TF-IDF** and **Cosine Similarity** on course titles.
* **Dynamic Pricing & Popularity Analysis:**
    * Suggests optimal pricing strategies (Conservative, Balanced, Premium) by analyzing similar courses.
    * Uses a **Bayesian Average** to calculate a `popularity_score`, preventing bias from courses with very few reviews.
* **SQL-Powered Analytics:** Leverages a SQL Server database for robust data storage and complex analytical queries, including predefined views for market gap analysis and subject performance.

## 💻 Tech Stack

* **Data Analysis & ML:** Python, Pandas, Scikit-learn (TF-IDF, Cosine Similarity)
* **Database:** SQL Server (T-SQL)
* **Web Application:** Streamlit
* **Python-DB Connector:** pyodbc
* **Data Exploration:** Jupyter Notebook

## 📂 Project Structure & Workflow

The project follows a clear workflow, represented by the key files:

1.  **`Data Exploration.ipynb`**
    * **Purpose:** The starting point of the project.
    * **Process:** Loads the raw `Udemy Courses.csv` dataset into a Pandas DataFrame.
    * Performs initial exploratory data analysis (EDA), data cleaning (handling nulls, checking types), and feature engineering (e.g., creating `price_category`, `quality_score`).
    * The cleaned data from this notebook is the source for the SQL database.

2.  **`SQL Queries.sql`**
    * **Purpose:** Sets up the entire database structure.
    * **Process:**
        * Creates the `udemy_courses` table schema.
        * Defines `NONCLUSTERED INDEX`es to optimize query performance.
        * Creates several analytical `VIEW`s (e.g., `vw_subject_performance`, `vw_market_gaps`) to pre-aggregate data for the dashboard.
        * Contains various ad-hoc queries used for analysis.

3.  **`Sql import.ipynb`**
    * **Purpose:** Migrates the cleaned data from the notebook into the SQL Server.
    * **Process:**
        * Connects to the SQL Server database.
        * Reads the cleaned CSV (from `Data Exploration.ipynb`).
        * Uses `pyodbc` and `pandas` to efficiently bulk-insert the data into the `udemy_courses` table.
        * Includes verification queries to ensure the data was imported correctly.

4.  **`recommendation_system.py`**
    * **Purpose:** The final interactive web application.
    * **Process:**
        * Connects to the SQL Server database using Streamlit's caching features (`@st.cache_resource`, `@st.cache_data`).
        * Loads data from the SQL views and main table.
        * Provides a UI for users to select a course.
        * Calculates and displays the top 10 most similar courses (content-based).
        * Calculates and displays pricing recommendations based on those similar courses.

## 🏁 Getting Started

To run this project locally, follow these steps:

### 1. Prerequisites

* Python 3.8+
* SQL Server (e.g., SQL Server Express)
* The original `Udemy Courses.csv` dataset (not included in this repo, can be found on Kaggle).

### 2. Database Setup

1.  Open SQL Server Management Studio (SSMS) or your preferred SQL client.
2.  Create a new database (e.g., `courses`).
3.  Open the **`SQL Queries.sql`** file and run the script against your new `courses` database. This will create the `udemy_courses` table and all the necessary views. You may skip the create table part if you have already imported the data.

### 3. Data Import

1.  Open the **`Sql import.ipynb`** notebook.
2.  Update the `conn_str` (connection string) in the notebook to point to your local SQL Server instance and `courses` database.
3.  Make sure the notebook points to the correct path of your `Udemy Courses.csv` file.
4.  Run the notebook cells to clean the data and import it into your `udemy_courses` table.

### 4. Install Dependencies

It's recommended to create a virtual environment:

```sh
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Create a requirements.txt file with the following content:
```
pandas
numpy
scikit-learn
streamlit
pyodbc
plotly
```
### 5. Run the Streamlit App
1. Open the recommendation_system.py file.

2. Update the conn_str in the get_connection() function to match your database credentials.

3. Run the app from your terminal:
```
streamlit run recommendation_system.py
```
Your browser should automatically open to the application.
