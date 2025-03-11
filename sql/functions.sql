DROP FUNCTION IF EXISTS get_cards_stat_by_period(text);
CREATE OR REPLACE FUNCTION get_cards_stat_by_period(
	period_type text)
    RETURNS TABLE(
		period timestamp without time zone, 
		nm_id integer, 
		open_card_count bigint, 
		add_to_cart_count bigint, 
		orders_count bigint, 
		orders_sum_rub double precision, 
		buyouts_count bigint, 
		buyouts_sum_rub double precision, 
		cancel_count bigint, 
		cancel_sum_rub double precision
	) 
    LANGUAGE 'plpgsql'
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, begin) AS period,
			nm_id as nm_id,
			sum(open_card_count) as open_card_count,
			sum(add_to_cart_count) as add_to_cart_count,
			sum(orders_count) as orders_count,
			sum(orders_sum_rub) as orders_sum_rub,
			sum(buyouts_count) as buyouts_count,
			sum(buyouts_sum_rub) as buyouts_sum_rub,
			sum(cancel_count) as cancel_count,
			sum(cancel_sum_rub) as cancel_sum_rub
        FROM cards_stat
        GROUP BY period, nm_id
        ORDER BY period, nm_id', 
        period_type);
END;
$$;


DROP FUNCTION IF EXISTS get_orders_by_period(text);
CREATE OR REPLACE FUNCTION get_orders_by_period(
	period_type text)
    RETURNS TABLE(
		period timestamp without time zone, 
		nm_id integer, 
		count bigint, 
		total_price double precision, 
		avg_total_price double precision, 
		avg_discount_percent double precision, 
		avg_spp double precision, 
		finished_price double precision, 
		avg_finished_price double precision, 
		price_with_disc double precision, 
		avg_price_with_disc double precision
	) 
    LANGUAGE 'plpgsql'
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, date) AS period,
			nm_id as nm_id,
            count(id) as count,
            sum(total_price) as total_price,
            avg(total_price) as avg_total_price,
            avg(discount_percent) as avg_discount_percent,
            avg(spp) as avg_spp,
            sum(finished_price) as finished_price,
            avg(finished_price) as avg_finished_price,
            sum(price_with_disc) as price_with_disc,
            avg(price_with_disc) as avg_price_with_disc
        FROM orders
        GROUP BY period, nm_id
        ORDER BY period, nm_id', 
        period_type);
END;
$$;


DROP FUNCTION IF EXISTS get_sales_by_period(text);
CREATE OR REPLACE FUNCTION get_sales_by_period(
	period_type text)
    RETURNS TABLE(
		period timestamp without time zone, 
		nm_id integer, 
		count bigint, 
		total_price double precision, 
		avg_total_price double precision, 
		avg_discount_percent double precision, 
		avg_spp double precision, 
		for_pay double precision, 
		avg_for_pay double precision, 
		finished_price double precision, 
		avg_finished_price double precision, 
		price_with_disc double precision, 
		avg_price_with_disc double precision
	) 
    LANGUAGE 'plpgsql'
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT 
			date_trunc(%L, date) AS period,
			nm_id as nm_id,
			count(id) as count,
			sum(total_price) as total_price,
			avg(total_price) as avg_total_price,
			avg(discount_percent) as avg_discount_percent,
			avg(spp) as avg_spp,
			sum(for_pay) as for_pay,
			avg(for_pay) as avg_for_pay,
			sum(finished_price) as finished_price,
			avg(finished_price) as avg_finished_price,
			sum(price_with_disc) as price_with_disc,
			avg(price_with_disc) as avg_price_with_disc
        FROM sales
        GROUP BY period, nm_id
        ORDER BY period, nm_id', 
        period_type);
END;
$$;


-- возмонжно last_change_date надо поменять на cancel_date
DROP FUNCTION IF EXISTS get_orders_cancelled_by_period(text);
CREATE OR REPLACE FUNCTION get_orders_cancelled_by_period(
	period_type text)
    RETURNS TABLE(
		period timestamp without time zone, 
		nm_id integer, 
		count bigint, 
		total_price double precision, 
		avg_total_price double precision, 
		avg_discount_percent double precision, 
		avg_spp double precision, 
		finished_price double precision, 
		avg_finished_price double precision, 
		price_with_disc double precision, 
		avg_price_with_disc double precision
	) 
    LANGUAGE 'plpgsql'

AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, cancel_date) AS period, 
			nm_id as nm_id,
            count(id) as count,
            sum(total_price) as total_price,
            avg(total_price) as avg_total_price,
            avg(discount_percent) as avg_discount_percent,
            avg(spp) as avg_spp,
            sum(finished_price) as finished_price,
            avg(finished_price) as avg_finished_price,
            sum(price_with_disc) as price_with_disc,
            avg(price_with_disc) as avg_price_with_disc
        FROM orders
		WHERE is_cancel = true
        GROUP BY period, nm_id
        ORDER BY period, nm_id', 
        period_type);
END;
$$;


DROP FUNCTION IF EXISTS get_pipeline_by_period(text);
CREATE OR REPLACE FUNCTION get_pipeline_by_period(
	period_type text)
    RETURNS TABLE(
		period TIMESTAMP,
	    nm_id INT,
    	open_card_count BIGINT,
	    add_to_cart_count BIGINT,
    	orders_count BIGINT,
	    orders_sum FLOAT,
    	sales_count BIGINT,
	    sales_sum FLOAT,
    	orders_cancelled_count BIGINT,
	    orders_cancelled_sum FLOAT
	) 
    LANGUAGE 'plpgsql'
AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT 
            cs.period,
            cs.nm_id,
            cs.open_card_count,
            cs.add_to_cart_count,
            o.count as orders_count,
            o.price_with_disc as orders_sum,
            s.count as sales_count,
            s.price_with_disc as sales_sum,
            oc.count as orders_cancelled_count,
            oc.price_with_disc as orders_cancelled_sum
        FROM get_cards_stat_by_period(%L) cs
        LEFT JOIN get_orders_by_period(%L) o ON o.nm_id = cs.nm_id AND o.period = cs.period
        LEFT JOIN get_sales_by_period(%L) s ON s.nm_id = cs.nm_id AND s.period = cs.period
        LEFT JOIN get_orders_cancelled_by_period(%L) oc ON oc.nm_id = cs.nm_id AND oc.period = cs.period',
        period_type, period_type, period_type, period_type);
END;
$$;


-- DROP FUNCTION IF EXISTS get_pipeline_by_period_ttl(text);
-- CREATE OR REPLACE FUNCTION get_pipeline_by_period_ttl(
-- 	period_type text)
--     RETURNS TABLE(
-- 		period TIMESTAMP,
--     	open_card_count BIGINT,
-- 	    add_to_cart_count BIGINT,
--     	orders_count BIGINT,
-- 	    orders_sum FLOAT,
--     	sales_count BIGINT,
-- 	    sales_sum FLOAT,
--     	orders_cancelled_count BIGINT,
-- 	    orders_cancelled_sum FLOAT
-- 	) 
--     LANGUAGE 'plpgsql'

-- AS $$
-- BEGIN
--     RETURN QUERY EXECUTE format(
--         'SELECT 
--             period,
--             sum(open_card_count)::BIGINT as open_card_count,
--             sum(add_to_cart_count)::BIGINT as add_to_cart_count,
--             sum(orders_count)::BIGINT as orders_count,
--             sum(orders_sum) as orders_sum,
--             sum(sales_count)::BIGINT as sales_count,
--             sum(sales_sum) as sales_sum,
--             sum(orders_cancelled_count)::BIGINT as orders_cancelled_count,
--             sum(orders_cancelled_sum) as orders_cancelled_sum
--         FROM get_pipeline_by_period(%L)
-- 		GROUP BY period',
--         period_type);
-- END;
-- $$;