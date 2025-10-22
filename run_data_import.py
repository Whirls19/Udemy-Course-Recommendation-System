import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy import create_engine, text
import toml
import re

print("Starting data import script...")

# --- 1. Load Secrets and Connect to Supabase ---
print("Loading secrets from secrets.toml...")
try:
    secrets = toml.load("secrets.toml")
    DB_HOST = secrets["DB_HOST"]
    DB_NAME = secrets["DB_NAME"]
    DB_USER = secrets["DB_USER"]
    DB_PASSWORD = secrets["DB_PASSWORD"]
    DB_PORT = secrets["DB_PORT"]
except Exception as e:
    print(f"Error: Could not read secrets.toml. Make sure it is in the same directory. {e}")
    exit()

print("Connecting to Supabase (PostgreSQL)...")
try:
    conn_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(conn_string)
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit()

# --- 2. Load and Clean Data (from Data Exploration.ipynb) ---
print("Loading Udemy Courses.csv...")
df = pd.read_csv('Udemy Courses.csv')

print("Cleaning data...")
df['price'].fillna(0, inplace=True)
df.dropna(subset=['course_title', 'subject'], inplace=True)

df['published_timestamp'] = pd.to_datetime(df['published_timestamp'])
df['published_year'] = df['published_timestamp'].dt.year
df['is_paid'] = df['is_paid'].astype(bool)

# --- 3. Feature Engineering (from Data Exploration.ipynb) ---
print("Engineering features...")
current_date = pd.to_datetime(datetime.now()).tz_localize('UTC')
df['course_age_months'] = (((current_date - df['published_timestamp']).dt.days) / 30).round(1)
df['review_rate'] = (df['num_reviews'] / df['num_subscribers']).replace([np.inf, -np.inf], 0).fillna(0)
df['avg_lecture_duration'] = (df['content_duration'] / df['num_lectures']).replace([np.inf, -np.inf], 0).fillna(0)
df['price_per_hour'] = (df['price'] / df['content_duration']).replace([np.inf, -np.inf], 0).fillna(0)

df['popularity_score'] = (
    0.4 * (df['num_subscribers'] / df['num_subscribers'].max()) +
    0.3 * (df['num_reviews'] / df['num_reviews'].max()) +
    0.3 * (df['review_rate'] / df['review_rate'].max())
)
df['quality_score'] = (
    0.5 * (df['num_reviews'] / df['num_reviews'].max()) +
    0.5 * (df['review_rate'] / df['review_rate'].max())
)

def categorize_length(duration):
    if duration < 2: return 'Short'
    elif duration < 10: return 'Medium'
    else: return 'Long'
df['length_category'] = df['content_duration'].apply(categorize_length)

def categorize_price(price):
    if price == 0: return 'Free'
    elif price < 50: return 'Budget'
    elif price < 100: return 'Mid-Range'
    else: return 'Premium'
df['price_category'] = df['price'].apply(categorize_price)

# Clean column names to be safe
df.columns = [re.sub(r'[^A-Za-z0-9_]+', '', col) for col in df.columns]

# --- THIS IS THE FIX ---
print("Dropping duplicate course_ids from the DataFrame...")
original_rows = len(df)
df.drop_duplicates(subset=['course_id'], keep='first', inplace=True)
new_rows = len(df)
print(f"Removed {original_rows - new_rows} duplicate rows. DataFrame now has {new_rows} unique rows.")
# --- END OF FIX ---

# Select only the columns that match your SQL table
final_columns = [
    'course_id', 'course_title', 'url', 'is_paid', 'price', 
    'num_subscribers', 'num_reviews', 'num_lectures', 'level', 
    'content_duration', 'published_timestamp', 'subject', 'published_year',
    'review_rate', 'avg_lecture_duration', 'price_per_hour',
    'popularity_score', 'quality_score', 'length_category', 'price_category'
]
# Ensure df_final is created *after* dropping duplicates
df_final = df[final_columns]

# --- 4. Upload Data to Supabase ---
print(f"Uploading {len(df_final)} rows to udemy_courses table...")
try:
    # First, empty the table without dropping it
    with engine.connect() as conn:
        print("Clearing old data from udemy_courses table (TRUNCATE)...")
        conn.execute(text("TRUNCATE TABLE udemy_courses;"))
        conn.commit()
        print("Old data cleared.")
    
    # Now, append the new data to the empty table
    df_final.to_sql('udemy_courses', engine, if_exists='append', index=False)
    print("Data upload complete!")
except Exception as e:
    print(f"Error uploading data: {e}")
    exit()

# --- 5. Verify Data by Running a Query ---
print("\nVerifying data upload...")
try:
    with engine.connect() as conn:
        result = pd.read_sql_query(text("SELECT subject, COUNT(*) FROM udemy_courses GROUP BY subject"), conn)
        print("Verification query successful:")
        print(result)
except Exception as e:
    print(f"Error verifying data: {e}")

print("\nScript finished successfully.")