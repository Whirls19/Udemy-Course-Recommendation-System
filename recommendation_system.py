import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

st.set_page_config(
    page_title="Udemy Course Intelligence",
    page_icon="📚",
    layout="wide"
)

@st.cache_resource
def get_connection():
    """Create PostgreSQL connection using Streamlit Secrets"""
    conn_string = (
        f"postgresql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}"
        f"@{st.secrets['DB_HOST']}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}"
    )
    conn = psycopg2.connect(conn_string)
    return conn

@st.cache_data
def load_data():
    """Load main course data from PostgreSQL"""
    conn = get_connection()
    query = "SELECT * FROM udemy_courses"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

@st.cache_data
def load_sql_view(view_name):
    """Load specific view from PostgreSQL"""
    conn = get_connection()
    # Basic sanitization to prevent SQL injection
    safe_view_name = "".join(c for c in view_name if c.isalnum() or c == '_')
    query = f"SELECT * FROM {safe_view_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def calculate_bayesian_average(df, score_col='popularity_score', count_col='num_reviews', min_reviews=10):
    """Calculate Bayesian average to handle courses with few reviews"""
    C = df[score_col].mean()
    m = min_reviews
    v = df[count_col]
    R = df[score_col]
    adjusted_score = (v / (v + m)) * R + (m / (v + m)) * C
    return adjusted_score

def calculate_confidence_level(num_reviews):
    """Calculate confidence level based on number of reviews"""
    if num_reviews >= 100:
        return 'High'
    elif num_reviews >= 20:
        return 'Medium'
    elif num_reviews >= 5:
        return 'Low'
    else:
        return 'Very Low'

def enhance_dataframe(df):
    """Add enhanced metrics to dataframe"""
    df = df.copy()
    df['bayesian_popularity'] = calculate_bayesian_average(df, 'popularity_score', 'num_reviews', min_reviews=10)
    
    if 'quality_score' in df.columns:
        df['bayesian_quality'] = calculate_bayesian_average(df, 'quality_score', 'num_reviews', min_reviews=10)
    
    df['confidence_level'] = df['num_reviews'].apply(calculate_confidence_level)
    df['engagement_per_subscriber'] = df.apply(
        lambda row: row['num_reviews'] / row['num_subscribers'] if row['num_subscribers'] > 0 else 0,
        axis=1
    )
    df['is_suspicious'] = (df['review_rate'] >= 0.99) & (df['num_subscribers'] < 50)
    
    return df

@st.cache_resource
def build_recommender(_df):
    """Build recommendation system using TF-IDF and cosine similarity"""
    df = _df.copy()
    df['content'] = df['course_title'].fillna('') + ' ' + df['subject'].fillna('')
    tfidf = TfidfVectorizer(stop_words='english', max_features=500)
    tfidf_matrix = tfidf.fit_transform(df['content'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cosine_sim, df

def get_recommendations(course_id, df, cosine_sim, n=5, min_reviews=5):
    """Get N similar courses based on content similarity"""
    try:
        idx = df[df['course_id'] == course_id].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:]
        
        recommendations = []
        for score_idx, similarity in sim_scores:
            course = df.iloc[score_idx]
            if (course['num_reviews'] >= min_reviews and not course.get('is_suspicious', False)):
                recommendations.append({
                    'course_id': course['course_id'],
                    'course_title': course['course_title'],
                    'subject': course['subject'],
                    'price': course['price'],
                    'num_subscribers': course['num_subscribers'],
                    'num_reviews': course['num_reviews'],
                    'bayesian_popularity': course.get('bayesian_popularity', course.get('popularity_score', 0)),
                    'confidence_level': course.get('confidence_level', 'Unknown'),
                    'similarity_score': similarity
                })
            if len(recommendations) >= n:
                break
        
        return pd.DataFrame(recommendations)
    except Exception as e:
        st.error(f"Error generating recommendations: {e}")
        return pd.DataFrame()

try:
    df_raw = load_data()
    df = enhance_dataframe(df_raw)
    cosine_sim, df_rec = build_recommender(df)
    df_rec = enhance_dataframe(df_rec)
except Exception as e:
    st.error(f"Database connection error: {e}")
    st.stop()

st.sidebar.title("📚 Udemy Course Intelligence")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Overview", "🔍 Course Explorer", "💡 Recommendations", "📊 Analytics", "💰 Price Optimizer"]
)

if page == "🏠 Overview":
    st.title("📚 Udemy Course Intelligence Platform")
    st.markdown("### Data-Driven Insights for Course Selection & Strategy")
    
    df_clean = df[~df['is_suspicious']]
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Courses", f"{len(df):,}")
    with col2:
        st.metric("Subjects", f"{df['subject'].nunique()}")
    with col3:
        st.metric("Total Subscribers", f"{df['num_subscribers'].sum():,.0f}")
    with col4:
        avg_price = df_clean[df_clean['price'] > 0]['price'].mean()
        st.metric("Avg Course Price", f"${avg_price:.2f}")
    with col5:
        st.metric("Avg Engagement", f"{df_clean['review_rate'].mean():.4f}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Subjects Overview")
        subject_counts = df['subject'].value_counts()
        fig = px.bar(
            x=subject_counts.values, 
            y=subject_counts.index, 
            orientation='h',
            labels={'x': 'Number of Courses', 'y': 'Subject'},
            color=subject_counts.values, 
            color_continuous_scale='Blues'
        )
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>Courses: %{x:,}<extra></extra>'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Price Distribution")
        fig = px.histogram(
            df[df['price'] > 0], 
            x='price', 
            nbins=30,
            labels={'price': 'Price ($)', 'count': 'Frequency'},
            color_discrete_sequence=['coral']
        )
        fig.update_traces(
            hovertemplate='Price: $%{x:.2f}<br>Count: %{y}<extra></extra>',
            marker=dict(line=dict(color='white', width=1))
        )
        fig.update_layout(
            showlegend=False, 
            height=400,
            bargap=0.1
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Paid vs Free Courses")
        paid_count = df[df['is_paid'] == 1].shape[0]
        free_count = df[df['is_paid'] == 0].shape[0]
        fig = px.pie(
            values=[paid_count, free_count], 
            names=['Paid', 'Free'],
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        fig.update_traces(
            hovertemplate='%{label}<br>Courses: %{value:,}<br>Percentage: %{percent}<extra></extra>'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Course Length Distribution")
        length_dist = df['length_category'].value_counts()
        fig = px.pie(
            values=length_dist.values, 
            names=length_dist.index,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(
            hovertemplate='%{label}<br>Courses: %{value:,}<br>Percentage: %{percent}<extra></extra>'
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📈 Key Insights")
    
    top_subject = df['subject'].value_counts().index[0]
    avg_price_paid = df_clean[df_clean['price'] > 0]['price'].mean()
    best_engagement = df_clean[df_clean['num_reviews'] >= 10].nlargest(1, 'bayesian_popularity')['course_title'].values[0]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Most Popular Subject:** {top_subject}")
    with col2:
        st.success(f"**Average Price Point:** ${avg_price_paid:.2f}")
    with col3:
        st.warning(f"**Highest Engagement:** {best_engagement[:40]}...")

elif page == "🔍 Course Explorer":
    st.title("🔍 Course Explorer")
    st.markdown("Filter and explore courses based on your criteria")
    
    show_all = st.checkbox("Show all courses (including low-confidence)", value=False)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        subjects = ['All'] + sorted(df['subject'].dropna().unique().tolist())
        selected_subject = st.selectbox("Subject", subjects)
    
    with col2:
        levels = ['All'] + sorted(df['level'].dropna().unique().tolist())
        selected_level = st.selectbox("Level", levels)
    
    with col3:
        price_cats = ['All'] + sorted(df['price_category'].dropna().unique().tolist())
        selected_price = st.selectbox("Price Category", price_cats)
    
    min_price, max_price = st.slider(
        "Price Range ($)",
        min_value=0,
        max_value=int(df['price'].max()),
        value=(0, int(df['price'].max()))
    )
    
    filtered_df = df.copy()
    
    if not show_all:
        filtered_df = filtered_df[~filtered_df['is_suspicious']]
        filtered_df = filtered_df[filtered_df['num_reviews'] >= 3]
    
    if selected_subject != 'All':
        filtered_df = filtered_df[filtered_df['subject'] == selected_subject]
    if selected_level != 'All':
        filtered_df = filtered_df[filtered_df['level'] == selected_level]
    if selected_price != 'All':
        filtered_df = filtered_df[filtered_df['price_category'] == selected_price]
    
    filtered_df = filtered_df[(filtered_df['price'] >= min_price) & (filtered_df['price'] <= max_price)]
    
    st.markdown(f"### Found {len(filtered_df)} courses")
    
    sort_by = st.selectbox("Sort by", 
                          ['Bayesian Popularity', 'Number of Subscribers', 'Price', 'Bayesian Quality', 'Reviews'])
    
    sort_map = {
        'Bayesian Popularity': 'bayesian_popularity',
        'Number of Subscribers': 'num_subscribers',
        'Price': 'price',
        'Bayesian Quality': 'bayesian_quality',
        'Reviews': 'num_reviews'
    }
    
    filtered_df = filtered_df.sort_values(by=sort_map[sort_by], ascending=False)
    
    for idx, row in filtered_df.head(20).iterrows():
        confidence_emoji = {
            'High': '🟢',
            'Medium': '🟡',
            'Low': '🟠',
            'Very Low': '🔴'
        }.get(row['confidence_level'], '⚪')
        
        with st.expander(f"{confidence_emoji} **{row['course_title']}** - ${row['price']:.2f}"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Subscribers", f"{row['num_subscribers']:,}")
            with col2:
                st.metric("Reviews", f"{row['num_reviews']:,}")
            with col3:
                st.metric("Engagement", f"{row['review_rate']:.4f}")
            with col4:
                st.metric("Confidence", row['confidence_level'])
            
            st.write(f"**Subject:** {row['subject']} | **Level:** {row['level']} | **Duration:** {row['content_duration']:.1f} hrs")
            st.write(f"**Lectures:** {row['num_lectures']} | **Published:** {row['published_timestamp']}")
            if row.get('is_suspicious', False):
                st.warning("⚠️ This course may have suspicious metrics")
            if pd.notna(row['url']):
                st.markdown(f"[View Course]({row['url']})")

elif page == "💡 Recommendations":
    st.title("💡 Course Recommendation Engine")
    st.markdown("Get personalized course recommendations based on similarity")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Recommendation Quality Settings:**")
    with col2:
        min_reviews_filter = st.number_input("Min Reviews", min_value=1, max_value=50, value=5)
    
    course_titles = df['course_title'].tolist()
    selected_course = st.selectbox("Select a course to get recommendations:", course_titles)
    
    if st.button("Get Recommendations"):
        course_id = df[df['course_title'] == selected_course]['course_id'].values[0]
        
        st.subheader("Selected Course:")
        selected = df[df['course_id'] == course_id].iloc[0]
        st.info(f"**{selected['course_title']}** | {selected['subject']} | ${selected['price']:.2f} | Reviews: {selected['num_reviews']:,}")
        
        st.subheader("Recommended Similar Courses:")
        recommendations = get_recommendations(course_id, df_rec, cosine_sim, n=10, min_reviews=min_reviews_filter)
        
        if not recommendations.empty:
            for idx, row in recommendations.iterrows():
                confidence_emoji = {
                    'High': '🟢',
                    'Medium': '🟡',
                    'Low': '🟠',
                    'Very Low': '🔴'
                }.get(row['confidence_level'], '⚪')
                
                with st.container():
                    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                    with col1:
                        st.write(f"{confidence_emoji} **{row['course_title']}**")
                        st.caption(f"{row['subject']}")
                    with col2:
                        st.metric("Price", f"${row['price']:.0f}")
                    with col3:
                        st.metric("Subscribers", f"{row['num_subscribers']:,.0f}")
                    with col4:
                        st.metric("Reviews", f"{row['num_reviews']:,.0f}")
                    with col5:
                        st.metric("Match", f"{row['similarity_score']:.0%}")
                    st.markdown("---")
        else:
            st.warning("No recommendations found with current quality filters. Try lowering the minimum review requirement.")
    
    st.markdown("---")
    st.subheader("Or explore by subject:")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        subject = st.selectbox("Choose a subject:", sorted(df['subject'].unique()))
    with col2:
        min_subject_reviews = st.number_input("Min Reviews", min_value=1, max_value=100, value=10, key='subject_reviews')
    
    filtered_subject = df[(df['subject'] == subject) & 
                          (df['num_reviews'] >= min_subject_reviews) & 
                          (~df['is_suspicious'])]
    
    top_in_subject = filtered_subject.nlargest(10, 'bayesian_popularity')
    
    st.markdown(f"### Top 10 courses in {subject}")
    if len(top_in_subject) > 0:
        display_df = top_in_subject[['course_title', 'price', 'num_subscribers', 'num_reviews', 
                                     'bayesian_popularity', 'confidence_level']].copy()
        display_df.columns = ['Course', 'Price', 'Subscribers', 'Reviews', 'Score (Bayesian)', 'Confidence']
        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning(f"No courses found with at least {min_subject_reviews} reviews. Try lowering the threshold.")

elif page == "📊 Analytics":
    st.title("📊 Advanced Analytics")
    
    df_analytics = df[~df['is_suspicious']]
    
    tab1, tab2, tab3, tab4 = st.tabs(["Subject Analysis", "Pricing Insights", "Engagement Metrics", "Trends"])
    
    with tab1:
        st.subheader("Subject Performance Analysis")
        
        min_reviews_analytics = st.slider("Minimum reviews for analysis", 1, 50, 5)
        df_subject_analysis = df_analytics[df_analytics['num_reviews'] >= min_reviews_analytics]
        
        subject_perf = df_subject_analysis.groupby('subject').agg({
            'course_id': 'count',
            'price': 'mean',
            'num_subscribers': ['sum', 'mean'],
            'num_reviews': 'mean',
            'review_rate': 'mean',
            'bayesian_popularity': 'mean'
        }).round(2)
        
        subject_perf.columns = ['Course Count', 'Avg Price', 'Total Subscribers', 
                                'Avg Subscribers', 'Avg Reviews', 'Avg Engagement', 'Avg Bayesian Score']
        subject_perf = subject_perf.sort_values('Total Subscribers', ascending=False)
        
        fig = px.bar(
            subject_perf.reset_index(), 
            x='subject', 
            y='Total Subscribers',
            color='Avg Bayesian Score', 
            color_continuous_scale='Viridis',
            labels={'subject': 'Subject', 'Total Subscribers': 'Total Subscribers'}
        )
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Total Subscribers: %{y:,}<br>Avg Bayesian Score: %{marker.color:.2f}<extra></extra>'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(subject_perf, use_container_width=True)
    
    with tab2:
        st.subheader("Pricing Strategy Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            quality_courses = df_analytics[(df_analytics['price'] > 0) & 
                                          (df_analytics['num_reviews'] >= 5)]
            sample_df = quality_courses.sample(min(500, len(quality_courses)))
            fig = px.scatter(
                sample_df, 
                x='price', 
                y='num_subscribers',
                color='subject', 
                size='num_reviews',
                hover_data=['course_title', 'confidence_level'],
                labels={'price': 'Price ($)', 'num_subscribers': 'Subscribers'}
            )
            fig.update_traces(
                hovertemplate='<b>%{customdata[0]}</b><br>Price: $%{x:.2f}<br>Subscribers: %{y:,}<br>Reviews: %{marker.size:,}<br>Subject: %{fullData.name}<br>Confidence: %{customdata[1]}<extra></extra>'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            avg_price_subject = df_analytics[df_analytics['price'] > 0].groupby('subject')['price'].mean().sort_values(ascending=False)
            fig = px.bar(
                x=avg_price_subject.values, 
                y=avg_price_subject.index,
                orientation='h', 
                labels={'x': 'Average Price ($)', 'y': 'Subject'},
                color=avg_price_subject.values, 
                color_continuous_scale='Oranges'
            )
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>Average Price: $%{x:.2f}<extra></extra>'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Performance by Price Category")
        price_analysis = df_analytics.groupby('price_category').agg({
            'course_id': 'count',
            'num_subscribers': 'mean',
            'review_rate': 'mean',
            'bayesian_popularity': 'mean'
        }).round(2)
        price_analysis.columns = ['Courses', 'Avg Subscribers', 'Avg Engagement', 'Avg Bayesian Score']
        st.dataframe(price_analysis, use_container_width=True)
    
    with tab3:
        st.subheader("Engagement Metrics")
        
        st.markdown("### Most Engaging Courses (Bayesian Adjusted)")
        top_engagement = df_analytics[(df_analytics['num_subscribers'] > 100) & 
                                     (df_analytics['num_reviews'] >= 10)].nlargest(20, 'bayesian_popularity')
        
        fig = px.scatter(
            top_engagement, 
            x='num_subscribers', 
            y='review_rate',
            size='num_reviews', 
            color='subject',
            hover_data=['course_title', 'price', 'confidence_level'],
            labels={'num_subscribers': 'Subscribers', 'review_rate': 'Engagement Rate'}
        )
        fig.update_traces(
            hovertemplate='<b>%{customdata[0]}</b><br>Subscribers: %{x:,}<br>Engagement Rate: %{y:.4f}<br>Reviews: %{marker.size:,}<br>Price: $%{customdata[1]:.2f}<br>Subject: %{fullData.name}<br>Confidence: %{customdata[2]}<extra></extra>'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Correlation Matrix")
        corr_cols = ['price', 'num_subscribers', 'num_reviews', 'content_duration', 
                    'review_rate', 'bayesian_popularity', 'engagement_per_subscriber']
        corr_matrix = df_analytics[corr_cols].corr()
        
        fig = px.imshow(
            corr_matrix, 
            text_auto='.2f', 
            aspect='auto',
            color_continuous_scale='RdBu_r', 
            zmin=-1, 
            zmax=1
        )
        fig.update_traces(
            hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.2f}<extra></extra>'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("Publishing Trends Over Time")
        
        yearly = df_analytics.groupby('published_year').agg({
            'course_id': 'count',
            'price': 'mean',
            'num_subscribers': 'mean',
            'bayesian_popularity': 'mean'
        }).reset_index()
        yearly.columns = ['Year', 'Courses Published', 'Avg Price', 'Avg Subscribers', 'Avg Bayesian Score']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                yearly, 
                x='Year', 
                y='Courses Published',
                markers=True, 
                labels={'Courses Published': 'Number of Courses'}
            )
            fig.update_traces(
                hovertemplate='Year: %{x}<br>Courses Published: %{y:,}<extra></extra>'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                yearly, 
                x='Year', 
                y='Avg Price',
                markers=True, 
                color_discrete_sequence=['coral'],
                labels={'Avg Price': 'Average Price ($)'}
            )
            fig.update_traces(
                hovertemplate='Year: %{x}<br>Average Price: $%{y:.2f}<extra></extra>'
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

elif page == "💰 Price Optimizer":
    st.title("💰 Intelligent Price Optimizer")
    st.markdown("Find the optimal price point for your course based on historical data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        input_subject = st.selectbox("Course Subject", sorted(df['subject'].unique()))
    with col2:
        input_level = st.selectbox("Course Level", sorted(df['level'].unique()))
    
    input_duration = st.slider("Course Duration (hours)", 0.5, 50.0, 10.0, 0.5)
    input_lectures = st.number_input("Number of Lectures", min_value=5, max_value=500, value=50)
    
    min_reviews_price = st.slider("Minimum reviews for analysis", 1, 50, 10)
    
    if st.button("Calculate Optimal Price"):
        similar = df[
            (df['subject'] == input_subject) &
            (df['level'] == input_level) &
            (df['price'] > 0) &
            (df['num_reviews'] >= min_reviews_price) &
            (~df['is_suspicious'])
        ]
        
        if len(similar) > 0:
            st.success(f"Found {len(similar)} similar quality courses for analysis")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                median_price = similar['price'].median()
                st.metric("Median Price", f"${median_price:.2f}")
            
            with col2:
                mean_price = similar['price'].mean()
                st.metric("Average Price", f"${mean_price:.2f}")
            
            with col3:
                top_performers = similar.nlargest(max(1, int(len(similar) * 0.1)), 'bayesian_popularity')
                optimal_price = top_performers['price'].median()
                st.metric("Optimal Price (Top 10% Bayesian)", f"${optimal_price:.2f}", 
                         delta=f"{((optimal_price - mean_price) / mean_price * 100):.1f}%")
            
            st.markdown("---")
            
            st.subheader("Price Distribution of Similar Quality Courses")
            fig = px.histogram(
                similar, 
                x='price', 
                nbins=20,
                labels={'price': 'Price ($)', 'count': 'Number of Courses'},
                color_discrete_sequence=['teal']
            )
            fig.update_traces(
                hovertemplate='Price Range: $%{x:.2f}<br>Courses: %{y}<extra></extra>',
                marker=dict(line=dict(color='white', width=1))
            )
            fig.update_layout(bargap=0.1)
            fig.add_vline(
                x=optimal_price, 
                line_dash="dash", 
                line_color="red",
                annotation_text="Optimal Price"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Top Performing Courses in This Category (by Bayesian Score)")
            top_10 = similar.nlargest(10, 'bayesian_popularity')[
                ['course_title', 'price', 'num_subscribers', 'num_reviews', 'bayesian_popularity', 'confidence_level']
            ]
            st.dataframe(top_10, use_container_width=True)
            
            st.markdown("---")
            st.subheader("💡 Pricing Recommendations")
            st.write(f"""
            Based on analysis of **{len(similar)}** similar quality courses (min {min_reviews_price} reviews):
            - **Conservative Strategy:** Price at **${similar['price'].quantile(0.25):.2f}** (25th percentile) to maximize reach
            - **Balanced Strategy:** Price at **${median_price:.2f}** (median) for competitive positioning
            - **Premium Strategy:** Price at **${optimal_price:.2f}** (top performers' median - Bayesian adjusted) for maximum revenue
            - **High-End Strategy:** Price at **${similar['price'].quantile(0.75):.2f}** (75th percentile) for exclusive positioning
            
            ℹ️ **Note:** These recommendations are based on courses with at least {min_reviews_price} reviews to ensure reliable data.
            """)
        else:
            st.error(f"No similar courses found with at least {min_reviews_price} reviews. Try adjusting your criteria or lowering the minimum review threshold.")
            st.markdown("---")
            st.markdown("Built with ❤️ using Python, SQL Server, Streamlit | Data Source: Udemy Courses Dataset")
            st.caption("📊 Enhanced with Bayesian scoring to prevent low-review bias and suspicious course filtering")
