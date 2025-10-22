
USE courses;
GO

DROP TABLE IF EXISTS udemy_courses;
GO

CREATE TABLE udemy_courses (
    course_id INT PRIMARY KEY,
    course_title NVARCHAR(500) NOT NULL,
    url NVARCHAR(500),
    is_paid BIT,
    price DECIMAL(10, 2),
    num_subscribers INT,
    num_reviews INT,
    num_lectures INT,
    level NVARCHAR(50),
    content_duration DECIMAL(10, 2),
    published_timestamp DATETIME2,
    subject NVARCHAR(100),
    published_year INT,
    review_rate DECIMAL(10, 6),
    avg_lecture_duration DECIMAL(10, 4),
    price_per_hour DECIMAL(10, 2),
    popularity_score DECIMAL(10, 6),
    quality_score DECIMAL(10, 6),
    length_category NVARCHAR(20),
    price_category NVARCHAR(20)
);
GO


CREATE NONCLUSTERED INDEX IX_subject ON udemy_courses(subject);
CREATE NONCLUSTERED INDEX IX_price ON udemy_courses(price);
CREATE NONCLUSTERED INDEX IX_level ON udemy_courses(level);
CREATE NONCLUSTERED INDEX IX_published_year ON udemy_courses(published_year);
CREATE NONCLUSTERED INDEX IX_popularity_score ON udemy_courses(popularity_score DESC);
GO

-- Create Views for Analysis

-- View 1: Subject Performance Analysis
CREATE OR ALTER VIEW vw_subject_performance AS
SELECT 
    subject,
    COUNT(*) as total_courses,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(CAST(num_reviews AS DECIMAL)), 0) as avg_reviews,
    ROUND(AVG(review_rate), 4) as avg_review_rate,
    ROUND(AVG(content_duration), 2) as avg_duration,
    SUM(num_subscribers) as total_subscribers,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    ROUND(AVG(quality_score), 4) as avg_quality
FROM udemy_courses
GROUP BY subject;
GO

-- View 2: Top Performing Courses
CREATE OR ALTER VIEW vw_top_courses AS
SELECT TOP 100
    course_id,
    course_title,
    subject,
    price,
    num_subscribers,
    num_reviews,
    review_rate,
    popularity_score,
    quality_score,
    length_category,
    price_category,
    RANK() OVER (ORDER BY popularity_score DESC) as popularity_rank,
    RANK() OVER (ORDER BY quality_score DESC) as quality_rank
FROM udemy_courses
WHERE num_subscribers > 100
ORDER BY popularity_score DESC;
GO

-- View 3: Pricing Strategy Analysis
CREATE OR ALTER VIEW vw_pricing_analysis AS
SELECT 
    subject,
    price_category,
    COUNT(*) as course_count,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
GROUP BY subject, price_category
HAVING COUNT(*) >= 5;
GO

-- View 4: Course Length Impact
CREATE OR ALTER VIEW vw_length_impact AS
SELECT 
    length_category,
    COUNT(*) as total_courses,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(CAST(num_reviews AS DECIMAL)), 0) as avg_reviews,
    ROUND(AVG(review_rate), 4) as avg_review_rate,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
GROUP BY length_category;
GO

-- View 5: Paid vs Free Analysis
CREATE OR ALTER VIEW vw_paid_vs_free AS
SELECT 
    CASE WHEN is_paid = 1 THEN 'Paid' ELSE 'Free' END as course_type,
    subject,
    COUNT(*) as course_count,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(CAST(num_reviews AS DECIMAL)), 0) as avg_reviews,
    ROUND(AVG(review_rate), 4) as avg_review_rate,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
GROUP BY is_paid, subject;
GO

-- View 6: Yearly Trends
CREATE OR ALTER VIEW vw_yearly_trends AS
SELECT 
    published_year,
    COUNT(*) as courses_published,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(content_duration), 2) as avg_duration,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
WHERE published_year IS NOT NULL
GROUP BY published_year;
GO

-- View 7: Market Gap Analysis
CREATE OR ALTER VIEW vw_market_gaps AS
SELECT 
    subject,
    COUNT(*) as course_count,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_demand,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    CASE 
        WHEN COUNT(*) < 50 AND AVG(CAST(num_subscribers AS DECIMAL)) > 1000 THEN 'High Opportunity'
        WHEN COUNT(*) < 100 AND AVG(CAST(num_subscribers AS DECIMAL)) > 500 THEN 'Medium Opportunity'
        ELSE 'Saturated'
    END as market_status
FROM udemy_courses
GROUP BY subject;
GO

-- View 8: Best Value Courses
CREATE OR ALTER VIEW vw_best_value_courses AS
SELECT TOP 100
    course_id,
    course_title,
    subject,
    price,
    num_subscribers,
    num_reviews,
    review_rate,
    quality_score,
    price_per_hour,
    CASE 
        WHEN price_per_hour > 0 THEN ROUND(quality_score / price_per_hour, 4)
        ELSE 0
    END as value_score
FROM udemy_courses
WHERE price > 0 
  AND num_reviews > 10
  AND quality_score > 0.3
ORDER BY value_score DESC;
GO

-- View 9: Success Patterns
CREATE OR ALTER VIEW vw_success_patterns AS
SELECT 
    subject,
    level,
    price_category,
    length_category,
    COUNT(*) as course_count,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    ROUND(AVG(quality_score), 4) as avg_quality,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers
FROM udemy_courses
GROUP BY subject, level, price_category, length_category
HAVING COUNT(*) >= 3;
GO

-- View 10: Category Breakdown
CREATE OR ALTER VIEW vw_category_breakdown AS
SELECT 
    price_category,
    length_category,
    COUNT(*) as course_count,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
GROUP BY price_category, length_category;
GO

-- ============================================
-- STEP 5: KEY ANALYTICAL QUERIES
-- ============================================
-- Query 1: Top 4 Subjects by Total Subscribers
SELECT TOP 4
    subject, 
    SUM(num_subscribers) as total_subscribers,
    COUNT(*) as course_count,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
GROUP BY subject
ORDER BY total_subscribers DESC;
GO

-- Query 2: Optimal Pricing by Subject (FIXED)
DECLARE @avg_subscribers DECIMAL(18,2);

SELECT @avg_subscribers = AVG(CAST(num_subscribers AS DECIMAL))
FROM udemy_courses;

SELECT 
    subject,
    COUNT(*) as total_courses,
    ROUND(AVG(CASE 
        WHEN num_subscribers > @avg_subscribers 
        THEN price 
        ELSE NULL 
    END), 2) as optimal_price,
    ROUND(AVG(price), 2) as overall_avg_price
FROM udemy_courses
WHERE is_paid = 1
GROUP BY subject
HAVING COUNT(*) >= 10
ORDER BY optimal_price DESC;
GO


-- Query 3: Engagement Leaders
SELECT TOP 20
    course_title,
    subject,
    num_subscribers,
    num_reviews,
    ROUND(review_rate, 4) as engagement_rate,
    price,
    quality_score
FROM udemy_courses
WHERE num_subscribers > 500
ORDER BY review_rate DESC;
GO

-- Query 4: Course Length Sweet Spot
SELECT 
    length_category,
    COUNT(*) as courses,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
GROUP BY length_category
ORDER BY avg_subscribers DESC;
GO

-- Query 5: Price vs Performance Correlation
SELECT 
    price_category,
    COUNT(*) as courses,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    ROUND(AVG(quality_score), 4) as avg_quality
FROM udemy_courses
GROUP BY price_category
ORDER BY avg_popularity DESC;
GO

-- Query 6: Recent vs Old Courses Performance
SELECT 
    CASE 
        WHEN published_year >= 2016 THEN '2016-2017 (Recent)'
        WHEN published_year >= 2014 THEN '2014-2015'
        WHEN published_year >= 2012 THEN '2012-2013'
        WHEN published_year >= 2010 THEN '2010-2011'
        ELSE '2009 or Earlier'
    END as course_age_group,
    COUNT(*) as courses,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    MIN(published_year) as earliest_year,
    MAX(published_year) as latest_year
FROM udemy_courses
WHERE published_year IS NOT NULL
GROUP BY 
    CASE 
        WHEN published_year >= 2016 THEN '2016-2017 (Recent)'
        WHEN published_year >= 2014 THEN '2014-2015'
        WHEN published_year >= 2012 THEN '2012-2013'
        WHEN published_year >= 2010 THEN '2010-2011'
        ELSE '2009 or Earlier'
    END
ORDER BY earliest_year DESC;
GO
-- Query 7: Level-wise Performance
SELECT 
    level,
    COUNT(*) as courses,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(content_duration), 2) as avg_duration,
    ROUND(AVG(popularity_score), 4) as avg_popularity
FROM udemy_courses
GROUP BY level
ORDER BY avg_subscribers DESC;
GO

-- Query 8: Most Competitive Subjects
SELECT TOP 10
    subject,
    COUNT(*) as course_count,
    SUM(num_subscribers) as total_demand,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    'High Competition' as market_status
FROM udemy_courses
GROUP BY subject
HAVING COUNT(*) > 50
ORDER BY total_demand DESC;
GO

-- Query 9: Underserved Niches
SELECT TOP 10
    subject,
    level,
    price_category,
    COUNT(*) as course_count,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_demand,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    CASE 
        WHEN COUNT(*) < 50 AND AVG(CAST(num_subscribers AS DECIMAL)) > 1000 THEN 'High Opportunity'
        WHEN COUNT(*) < 100 AND AVG(CAST(num_subscribers AS DECIMAL)) > 800 THEN 'Medium Opportunity'
        ELSE 'Competitive'
    END as market_status
FROM udemy_courses
GROUP BY subject, level, price_category
HAVING COUNT(*) < 150  -- Look for less crowded combinations
ORDER BY 
    (AVG(CAST(num_subscribers AS DECIMAL)) * 1.0 / NULLIF(COUNT(*), 0)) DESC;  -- High demand per course
GO
-- Query 10: Premium Courses Analysis
SELECT 
    subject,
    COUNT(*) as premium_courses,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    ROUND(AVG(review_rate), 4) as avg_engagement,
    ROUND(AVG(price), 2) as avg_price,
    ROUND(AVG(quality_score), 4) as avg_quality
FROM udemy_courses
WHERE price > 100
GROUP BY subject
HAVING COUNT(*) >= 3
ORDER BY avg_subscribers DESC;
GO

-- Query 11: Price Per Hour Analysis
SELECT 
    subject,
    price_category,
    ROUND(AVG(price_per_hour), 2) as avg_price_per_hour,
    ROUND(AVG(CAST(num_subscribers AS DECIMAL)), 0) as avg_subscribers,
    COUNT(*) as course_count
FROM udemy_courses
WHERE price_per_hour > 0
GROUP BY subject, price_category
HAVING COUNT(*) >= 5
ORDER BY avg_subscribers DESC;
GO

-- Query 12: Quality vs Popularity Comparison
SELECT 
    subject,
    ROUND(AVG(quality_score), 4) as avg_quality,
    ROUND(AVG(popularity_score), 4) as avg_popularity,
    ROUND(AVG(quality_score) - AVG(popularity_score), 4) as quality_popularity_gap,
    COUNT(*) as course_count
FROM udemy_courses
GROUP BY subject
HAVING COUNT(*) >= 10
ORDER BY quality_popularity_gap DESC;
GO