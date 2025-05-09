
-- Competitions and Categories Queries

-- 1. List all competitions with their category name
SELECT c.competition_name, cat.category_name
FROM Competitions c
JOIN Categories cat ON c.category_id = cat.category_id;

-- 2. Count the number of competitions in each category
SELECT cat.category_name, COUNT(*) AS competition_count
FROM Competitions c
JOIN Categories cat ON c.category_id = cat.category_id
GROUP BY cat.category_name;

-- 3. Competitions of type 'doubles'
SELECT competition_name
FROM Competitions
WHERE type = 'doubles';

-- 4. Competitions in category 'ITF Men'
SELECT c.competition_name
FROM Competitions c
JOIN Categories cat ON c.category_id = cat.category_id
WHERE cat.category_name = 'ITF Men';

-- 5. Parent competitions and their sub-competitions
SELECT parent.competition_name AS parent_competition, child.competition_name AS sub_competition
FROM Competitions parent
JOIN Competitions child ON parent.competition_id = child.parent_id;

-- 6. Distribution of competition types by category
SELECT cat.category_name, c.type, COUNT(*) AS type_count
FROM Competitions c
JOIN Categories cat ON c.category_id = cat.category_id
GROUP BY cat.category_name, c.type;

-- 7. Competitions with no parent (top-level competitions)
SELECT competition_name
FROM Competitions
WHERE parent_id IS NULL;


-- Complexes and Venues Queries

-- 1. List all venues along with their associated complex name
SELECT v.venue_name, c.complex_name
FROM Venues v
JOIN Complexes c ON v.complex_id = c.complex_id;

-- 2. Count the number of venues in each complex
SELECT c.complex_name, COUNT(v.venue_id) AS venue_count
FROM Venues v
JOIN Complexes c ON v.complex_id = c.complex_id
GROUP BY c.complex_name;

-- 3. Get details of venues in a specific country (e.g., Chile)
SELECT venue_name, city_name, country_name, timezone
FROM Venues
WHERE country_name = 'Chile';

-- 4. Identify all venues and their timezones
SELECT venue_name, timezone
FROM Venues;

-- 5. Find complexes with more than one venue
SELECT c.complex_name, COUNT(v.venue_id) AS venue_count
FROM Venues v
JOIN Complexes c ON v.complex_id = c.complex_id
GROUP BY c.complex_name
HAVING venue_count > 1;

-- 6. List venues grouped by country
SELECT country_name, COUNT(venue_id) AS venue_count
FROM Venues
GROUP BY country_name
ORDER BY venue_count DESC;

-- 7. Find all venues for a specific complex (e.g., Nacional)
SELECT v.venue_name, c.complex_name, v.city_name, v.country_name, v.timezone
FROM Venues v
JOIN Complexes c ON v.complex_id = c.complex_id
WHERE c.complex_name = 'Nacional';


-- Competitors and Competitor_Rankings Queries

-- 1. Get all competitors with their rank and points
SELECT c.name, cr.rank, cr.points
FROM Competitors c
JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id;

-- 2. Find competitors ranked in the top 5
SELECT c.name, cr.rank, cr.points
FROM Competitors c
JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
WHERE cr.rank <= 5;

-- 3. List competitors with no rank movement (stable rank)
SELECT c.name, cr.rank, cr.movement
FROM Competitors c
JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
WHERE cr.movement = 0;

-- 4. Get the total points of competitors from a specific country (e.g., Croatia)
SELECT SUM(cr.points) AS total_points
FROM Competitors c
JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
WHERE c.country = 'Croatia';

-- 5. Count the number of competitors per country
SELECT c.country, COUNT(*) AS num_competitors
FROM Competitors c
GROUP BY c.country;

-- 6. Find competitors with the highest points
SELECT c.name, cr.rank, cr.points
FROM Competitors c
JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
ORDER BY cr.points DESC
LIMIT 3;
