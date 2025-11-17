-- ============================================
-- RushRadar Database Schema
-- Purpose: Predict wait times, item sales, and busyness levels
-- ============================================
-- 1. MENU ITEMS TABLE
-- Stores all menu items with pricing and categorization
CREATE TABLE menu_items (
	item_id SERIAL PRIMARY KEY,
	item_name VARCHAR(255) NOT NULL,
	category VARCHAR(100) NOT NULL,
	subcategory VARCHAR(100),
	price DECIMAL(10, 2) NOT NULL,
	description TEXT,
	is_active BOOLEAN DEFAULT TRUE,
	prep_time_minutes INTEGER,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT positive_price CHECK (price >= 0),
	CONSTRAINT positive_prep_time CHECK (prep_time_minutes >= 0)
);

CREATE INDEX idx_menu_items_category ON menu_items (category);

CREATE INDEX idx_menu_items_active ON menu_items (is_active);

-- 2. ORDERS TABLE
-- Stores order-level information including timing and party details
CREATE TABLE orders (
	order_id SERIAL PRIMARY KEY,
	order_timestamp TIMESTAMP NOT NULL,
	party_size INTEGER NOT NULL,
	order_total DECIMAL(10, 2) NOT NULL,
	subtotal DECIMAL(10, 2) NOT NULL,
	tax_amount DECIMAL(10, 2),
	tip_amount DECIMAL(10, 2),
	order_type VARCHAR(50) NOT NULL, -- 'dine_in', 'takeout', 'delivery'
	table_number VARCHAR(20),
	server_id INTEGER,
	order_status VARCHAR(50) DEFAULT 'completed', -- 'completed', 'cancelled', 'refunded'
	duration_minutes INTEGER, -- Time from order to completion
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT positive_party_size CHECK (party_size > 0),
	CONSTRAINT positive_order_total CHECK (order_total >= 0),
	CONSTRAINT valid_order_type CHECK (order_type IN ('dine_in', 'takeout', 'delivery'))
);

CREATE INDEX idx_orders_timestamp ON orders (order_timestamp);

CREATE INDEX idx_orders_date ON orders (DATE(order_timestamp));

CREATE INDEX idx_orders_type ON orders (order_type);

CREATE INDEX idx_orders_status ON orders (order_status);

-- 3. ORDER ITEMS TABLE (Junction Table)
-- Links orders to menu items with quantity and pricing details
CREATE TABLE order_items (
	order_item_id SERIAL PRIMARY KEY,
	order_id INTEGER NOT NULL,
	item_id INTEGER NOT NULL,
	quantity INTEGER NOT NULL DEFAULT 1,
	unit_price DECIMAL(10, 2) NOT NULL,
	item_total DECIMAL(10, 2) NOT NULL,
	special_instructions TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT fk_order FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
	CONSTRAINT fk_item FOREIGN KEY (item_id) REFERENCES menu_items (item_id) ON DELETE RESTRICT,
	CONSTRAINT positive_quantity CHECK (quantity > 0),
	CONSTRAINT positive_unit_price CHECK (unit_price >= 0)
);

CREATE INDEX idx_order_items_order ON order_items (order_id);

CREATE INDEX idx_order_items_item ON order_items (item_id);

CREATE INDEX idx_order_items_composite ON order_items (order_id, item_id);

-- 4. WAIT TIMES TABLE
-- Logs quoted wait times vs actual wait times for busyness prediction
CREATE TABLE wait_times (
	wait_time_id SERIAL PRIMARY KEY,
	log_timestamp TIMESTAMP NOT NULL,
	party_size INTEGER NOT NULL,
	quoted_wait_minutes INTEGER NOT NULL,
	actual_wait_minutes INTEGER,
	seated_timestamp TIMESTAMP,
	day_of_week INTEGER, -- 0=Sunday, 6=Saturday
	hour_of_day INTEGER,
	current_party_count INTEGER, -- Snapshot of restaurant occupancy
	current_table_occupancy_pct DECIMAL(5, 2), -- Percentage of tables occupied
	wait_type VARCHAR(50) DEFAULT 'walk_in', -- 'walk_in', 'reservation', 'call_ahead'
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT positive_party_size CHECK (party_size > 0),
	CONSTRAINT positive_quoted_wait CHECK (quoted_wait_minutes >= 0),
	CONSTRAINT positive_actual_wait CHECK (
		actual_wait_minutes IS NULL
		OR actual_wait_minutes >= 0
	),
	CONSTRAINT valid_day CHECK (day_of_week BETWEEN 0 AND 6),
	CONSTRAINT valid_hour CHECK (hour_of_day BETWEEN 0 AND 23),
	CONSTRAINT valid_occupancy CHECK (current_table_occupancy_pct BETWEEN 0 AND 100)
);

CREATE INDEX idx_wait_times_timestamp ON wait_times (log_timestamp);

CREATE INDEX idx_wait_times_date ON wait_times (DATE(log_timestamp));

CREATE INDEX idx_wait_times_day_hour ON wait_times (day_of_week, hour_of_day);

CREATE INDEX idx_wait_times_party_size ON wait_times (party_size);

-- 5. EXTERNAL FACTORS TABLE
-- Daily log of weather conditions and local events affecting restaurant traffic
CREATE TABLE external_factors (
	factor_id SERIAL PRIMARY KEY,
	factor_date DATE NOT NULL UNIQUE,
	day_of_week INTEGER NOT NULL,
	is_holiday BOOLEAN DEFAULT FALSE,
	holiday_name VARCHAR(100),
	weather_condition VARCHAR(50), -- 'sunny', 'rainy', 'snowy', 'cloudy'
	temperature_high_f DECIMAL(5, 2),
	temperature_low_f DECIMAL(5, 2),
	precipitation_inches DECIMAL(5, 2) DEFAULT 0,
	local_event_name VARCHAR(255),
	local_event_type VARCHAR(100), -- 'sports', 'concert', 'festival', 'conference'
	event_attendance_estimated INTEGER,
	event_distance_miles DECIMAL(5, 2), -- Distance from restaurant
	is_weekend BOOLEAN GENERATED ALWAYS AS (day_of_week IN (0, 6)) STORED,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT valid_day CHECK (day_of_week BETWEEN 0 AND 6),
	CONSTRAINT positive_precipitation CHECK (precipitation_inches >= 0)
);

CREATE INDEX idx_external_factors_date ON external_factors (factor_date);

CREATE INDEX idx_external_factors_holiday ON external_factors (is_holiday);

CREATE INDEX idx_external_factors_weekend ON external_factors (is_weekend);

CREATE INDEX idx_external_factors_weather ON external_factors (weather_condition);

-- ============================================
-- OPTIONAL: AGGREGATE VIEWS FOR ANALYTICS
-- ============================================
-- View: Hourly busyness metrics
CREATE VIEW hourly_busyness AS
SELECT
	DATE(order_timestamp) AS order_date,
	EXTRACT(
		HOUR
		FROM
			order_timestamp
	) AS hour_of_day,
	EXTRACT(
		DOW
		FROM
			order_timestamp
	) AS day_of_week,
	COUNT(DISTINCT order_id) AS total_orders,
	SUM(party_size) AS total_guests,
	SUM(order_total) AS total_revenue,
	AVG(duration_minutes) AS avg_order_duration
FROM
	orders
WHERE
	order_status = 'completed'
GROUP BY
	order_date,
	hour_of_day,
	day_of_week;

-- View: Item popularity and sales
CREATE VIEW item_sales_summary AS
SELECT
	mi.item_id,
	mi.item_name,
	mi.category,
	COUNT(oi.order_item_id) AS times_ordered,
	SUM(oi.quantity) AS total_quantity_sold,
	SUM(oi.item_total) AS total_revenue,
	AVG(oi.unit_price) AS avg_price
FROM
	menu_items mi
	LEFT JOIN order_items oi ON mi.item_id = oi.item_id
	LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE
	o.order_status = 'completed'
	OR o.order_status IS NULL
GROUP BY
	mi.item_id,
	mi.item_name,
	mi.category;