DROP INDEX IF EXISTS idx_orders_date_nmid;
CREATE INDEX idx_orders_date_nmid ON orders(date, nm_id);
DROP INDEX IF EXISTS idx_orders_cancel_date_nmid;
CREATE INDEX idx_orders_cancel_date_nmid ON orders(cancel_date, nm_id) WHERE is_cancel = true;
DROP INDEX IF EXISTS idx_cards_stat_begin_nmid;
CREATE INDEX idx_cards_stat_begin_nmid ON cards_stat(begin, nm_id);
DROP INDEX IF EXISTS idx_sales_date_nmid;
CREATE INDEX idx_sales_date_nmid ON sales(date, nm_id);


DROP FUNCTION IF EXISTS get_cards_stat_by_period(text);

CREATE OR REPLACE FUNCTION get_cards_stat_by_period(
    period_type text
)
RETURNS TABLE (
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
LANGUAGE plpgsql
AS $$
BEGIN
    -- Validation
    IF period_type NOT IN ('day', 'week', 'month') THEN
        RAISE EXCEPTION 'Invalid period_type: %, allowed values are day, week, month', period_type;
    END IF;

    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, begin) AS period,
            nm_id,
            sum(open_card_count),
            sum(add_to_cart_count),
            sum(orders_count),
            sum(orders_sum_rub),
            sum(buyouts_count),
            sum(buyouts_sum_rub),
            sum(cancel_count),
            sum(cancel_sum_rub)
        FROM cards_stat
        GROUP BY period, nm_id
        ORDER BY period, nm_id',
        period_type
    );
END;
$$;


DROP FUNCTION IF EXISTS get_orders_by_period(text);

CREATE OR REPLACE FUNCTION get_orders_by_period(
    period_type text
)
RETURNS TABLE (
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
LANGUAGE plpgsql
AS $$
BEGIN
    -- Validate period_type
    IF period_type NOT IN ('day', 'week', 'month') THEN
        RAISE EXCEPTION 'Invalid period_type: %, allowed values are day, week, month', period_type;
    END IF;

    -- Execute aggregation query
    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, date) AS period,
            nm_id,
            count(id),
            sum(total_price),
            avg(total_price),
            avg(discount_percent),
            avg(spp),
            sum(finished_price),
            avg(finished_price),
            sum(price_with_disc),
            avg(price_with_disc)
        FROM orders
        GROUP BY period, nm_id
        ORDER BY period, nm_id',
        period_type
    );
END;
$$;


DROP FUNCTION IF EXISTS get_orders_cancelled_by_period(text);

CREATE OR REPLACE FUNCTION get_orders_cancelled_by_period(
    period_type text
)
RETURNS TABLE (
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
LANGUAGE plpgsql
AS $$
BEGIN
    -- Validate period_type
    IF period_type NOT IN ('day', 'week', 'month') THEN
        RAISE EXCEPTION 'Invalid period_type: %, allowed values are day, week, month', period_type;
    END IF;

    -- Execute aggregation query for canceled orders only
    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, cancel_date) AS period, 
            nm_id,
            count(id),
            sum(total_price),
            avg(total_price),
            avg(discount_percent),
            avg(spp),
            sum(finished_price),
            avg(finished_price),
            sum(price_with_disc),
            avg(price_with_disc)
        FROM orders
        WHERE is_cancel = true
        GROUP BY period, nm_id
        ORDER BY period, nm_id',
        period_type
    );
END;
$$;


DROP FUNCTION IF EXISTS get_sales_by_period(text);

CREATE OR REPLACE FUNCTION get_sales_by_period(period_type text)
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
    avg_price_with_disc double precision)
 LANGUAGE plpgsql
AS $$
BEGIN
    -- Validate period_type
    IF period_type NOT IN ('day', 'week', 'month') THEN
        RAISE EXCEPTION 'Invalid period_type: %, allowed values are day, week, month', period_type;
    END IF;

    -- Execute aggregation query
    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, date) AS period,
            nm_id,
            count(id),
			SUM(
                CASE WHEN total_price < 0 THEN
                    -total_price
                ELSE
                    total_price
                END
            ) AS total_price,
            AVG(
                CASE WHEN total_price < 0 THEN
                    -total_price
                ELSE
                    total_price
                END
            ) AS avg_total_price,
            avg(discount_percent),
            avg(spp),
			SUM(
                CASE WHEN for_pay < 0 THEN
                    -for_pay
                ELSE
                    for_pay
                END
            ) AS for_pay,
            AVG(
                CASE WHEN for_pay < 0 THEN
                    -for_pay
                ELSE
                    for_pay
                END
            ) AS avg_for_pay,
			SUM(
                CASE WHEN finished_price < 0 THEN
                    -finished_price
                ELSE
                    finished_price
                END
            ) AS finished_price,
            AVG(
                CASE WHEN finished_price < 0 THEN
                    -finished_price
                ELSE
                    finished_price
                END
            ) AS avg_finished_price,
			SUM(
                CASE WHEN price_with_disc < 0 THEN
                    -price_with_disc
                ELSE
                    price_with_disc
                END
            ) AS price_with_disc,
            AVG(
                CASE WHEN price_with_disc < 0 THEN
                    -price_with_disc
                ELSE
                    price_with_disc
                END
            ) AS avg_price_with_disc
        FROM sales
        GROUP BY period, nm_id
        ORDER BY period, nm_id',
        period_type
    );
END;
$$;


DROP FUNCTION get_sales_returned_by_period(text);

CREATE OR REPLACE FUNCTION get_sales_returned_by_period(period_type text)
 RETURNS TABLE(period timestamp without time zone, nm_id integer, count bigint, total_price double precision, avg_total_price double precision, avg_discount_percent double precision, avg_spp double precision, for_pay double precision, avg_for_pay double precision, finished_price double precision, avg_finished_price double precision, price_with_disc double precision, avg_price_with_disc double precision)
 LANGUAGE plpgsql
AS $$
BEGIN
    -- Validate period_type
    IF period_type NOT IN ('day', 'week', 'month') THEN
        RAISE EXCEPTION 'Invalid period_type: %, allowed values are day, week, month', period_type;
    END IF;

    -- Execute aggregation query
    RETURN QUERY EXECUTE format(
        'SELECT 
            date_trunc(%L, date) AS period,
            nm_id,
            count(id),
            -sum(total_price),
            -avg(total_price),
            avg(discount_percent),
            avg(spp),
            -sum(for_pay),
            -avg(for_pay),
            -sum(finished_price),
            -avg(finished_price),
            -sum(price_with_disc),
            -avg(price_with_disc)
        FROM sales
        WHERE price_with_disc < 0
        GROUP BY period, nm_id
        ORDER BY period, nm_id',
        period_type
    );
END;
$$;


DROP FUNCTION public.get_pipeline_by_period(text);

CREATE OR REPLACE FUNCTION public.get_pipeline_by_period(period_type text)
 RETURNS TABLE(period timestamp without time zone, nm_id integer, vendor_code varchar, open_card_count bigint, add_to_cart_count bigint, orders_count bigint, orders_sum double precision, sales_count bigint, sales_sum double precision, orders_cancelled_count bigint, orders_cancelled_sum double precision, sales_returned_count bigint, sales_returned_sum double precision)
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF period_type NOT IN ('day', 'week', 'month') THEN
        RAISE EXCEPTION 'Invalid period_type: %, allowed values: day, week, month', period_type;
    END IF;

    RETURN QUERY EXECUTE format(
        $$
        WITH all_periods_nmid AS (
            SELECT period, nm_id 
            FROM get_cards_stat_by_period(%L)
            UNION
            SELECT period, nm_id 
            FROM get_orders_by_period(%L)
            UNION
            SELECT period, nm_id 
            FROM get_sales_by_period(%L)
            UNION
            SELECT period, nm_id 
            FROM get_orders_cancelled_by_period(%L)
            UNION
            SELECT period, nm_id 
            FROM get_sales_returned_by_period(%L)
        )
        SELECT 
            p.period,
            p.nm_id,
			c.vendor_code,
            COALESCE(cs.open_card_count, 0)         AS open_card_count,
            COALESCE(cs.add_to_cart_count, 0)       AS add_to_cart_count,
            COALESCE(o.count, 0)                   AS orders_count,
            COALESCE(o.price_with_disc, 0)         AS orders_sum,
			COALESCE(s.count, 0) - COALESCE(sr.count, 0)					AS sales_count,
			COALESCE(s.price_with_disc, 0) - COALESCE(sr.price_with_disc, 0)			AS sales_sum,
            COALESCE(oc.count, 0)                  AS orders_cancelled_count,
            COALESCE(oc.price_with_disc, 0)        AS orders_cancelled_sum,
            COALESCE(sr.count, 0)                  AS sales_returned_count,
            COALESCE(sr.price_with_disc, 0)        AS sales_returned_sum
        FROM all_periods_nmid p
        LEFT JOIN get_cards_stat_by_period(%L) cs
            ON cs.period = p.period AND cs.nm_id = p.nm_id
        LEFT JOIN get_orders_by_period(%L) o
            ON o.period = p.period AND o.nm_id = p.nm_id
        LEFT JOIN get_sales_by_period(%L) s
            ON s.period = p.period AND s.nm_id = p.nm_id
        LEFT JOIN get_orders_cancelled_by_period(%L) oc
            ON oc.period = p.period AND oc.nm_id = p.nm_id
        LEFT JOIN get_sales_returned_by_period(%L) sr
            ON sr.period = p.period AND sr.nm_id = p.nm_id
		LEFT JOIN cards c
			ON c.nm_id = p.nm_id
        ORDER BY p.period, p.nm_id
        $$
        , period_type, period_type, period_type, period_type, period_type
        , period_type, period_type, period_type, period_type, period_type
    );
END;
$function$
;

DROP FUNCTION get_financial_report_by_period(text);
CREATE OR REPLACE FUNCTION get_financial_report_by_period(period_type text)
 RETURNS TABLE(
 	date_from timestamp without time zone, -- От
 	date_to timestamp without time zone, -- До
 	retail_price double precision, -- Цена розничная
 	retail_amount double precision, -- Вайлдберриз реализовал Товар (Пр)
 	sale_percent double precision, -- Согласованная скидка, %
 	ppvz_for_pay double precision, -- К перечислению продавцу за реализованный товар
 	delivery_rub double precision, -- Услуги по доставке товара покупателю
 	penalty double precision, -- Общая сумма штрафов
 	additional_payment double precision,-- Доплаты
 	storage_fee double precision, -- Стоимость хранения
 	acceptance double precision, -- Стоимость платной приёмки
 	deduction double precision, -- Прочие удержания/выплаты
 	ttl_for_pay double precision) -- Итоговая сумма выплаты
 LANGUAGE plpgsql
AS $$
BEGIN
	RETURN QUERY EXECUTE format(
		'select 
			min(fr.date_from) as date_from,
			max(fr.date_to) as date_to,
			sum(fr.retail_price) as retail_price,
			sum(fr.retail_amount) as retail_amount,
			sum(fr.sale_percent) as sale_percent,
			sum(fr.ppvz_for_pay) as ppvz_for_pay,
			sum(fr.delivery_rub) as delivery_rub,
			sum(fr.penalty) as penalty,
			sum(fr.additional_payment) as additional_payment,
			sum(fr.storage_fee) as storage_fee,
			sum(fr.acceptance) as acceptance,
			sum(fr.deduction) as deduction,
			sum(fr.ttl_for_pay) as ttl_for_pay,
            sum(fr.buying_price) as buying_price,
			sum(fr.ttl_for_pay) - sum(fr.buying_price) as profit
		from financial_report fr
		group by 
			date_trunc(%L, fr.date_from)
		order by
			date_from', period_type);
END
$$;


-- DROP FUNCTION get_financial_report_by_report_ids(report_ids int4[]);
-- CREATE OR REPLACE FUNCTION get_financial_report_by_report_ids(report_ids int4[])
--  RETURNS TABLE(
--  	nm_id int4,
--  	quantity double precision,
--  	retail_amount double precision,
--  	ppvz_for_pay double precision,
--  	penalty double precision,
--  	additional_payment double precision,
--  	delivery_rub double precision,
--  	storage_fee double precision,
--  	acceptance double precision,
--  	deduction double precision
--  )
--  LANGUAGE plpgsql
-- AS $$
-- begin
-- 	RETURN QUERY 
--     EXECUTE '
--         SELECT 
--             nm_id,
--             SUM(quantity)::double precision AS quantity,
--             SUM(retail_amount)::double precision AS retail_amount,
--             SUM(ppvz_for_pay)::double precision AS ppvz_for_pay,
--             SUM(penalty)::double precision AS penalty,
--             SUM(additional_payment)::double precision AS additional_payment,
--             SUM(delivery_rub)::double precision AS delivery_rub,
--             SUM(storage_fee)::double precision AS storage_fee,
--             SUM(acceptance)::double precision AS acceptance,
--             SUM(deduction)::double precision AS deduction
--         FROM financial_report_detailed
--         WHERE realizationreport_id = ANY($1)
--         GROUP BY nm_id
--         ORDER BY nm_id'
--     USING report_ids;
-- end
-- $$;


-- DROP FUNCTION public.get_financial_report_by_dates(timestamp, timestamp);
-- CREATE OR REPLACE FUNCTION public.get_financial_report_by_dates(date_from timestamp, date_to timestamp)
--  RETURNS TABLE(nm_id integer, quantity double precision, retail_amount double precision, ppvz_for_pay double precision, penalty double precision, additional_payment double precision, delivery_rub double precision, storage_fee double precision, acceptance double precision, deduction double precision)
--  LANGUAGE plpgsql
-- AS $$
-- begin
-- 	RETURN QUERY 
--     EXECUTE '
--         SELECT 
--             nm_id,
--             SUM(quantity)::double precision AS quantity,
--             SUM(retail_amount)::double precision AS retail_amount,
--             SUM(ppvz_for_pay)::double precision AS ppvz_for_pay,
--             SUM(penalty)::double precision AS penalty,
--             SUM(additional_payment)::double precision AS additional_payment,
--             SUM(delivery_rub)::double precision AS delivery_rub,
--             SUM(storage_fee)::double precision AS storage_fee,
--             SUM(acceptance)::double precision AS acceptance,
--             SUM(deduction)::double precision AS deduction
--         FROM financial_report_detailed
--         WHERE rr_dt >= $1 and rr_dt <= $2
--         GROUP BY nm_id
--         ORDER BY nm_id'
--     USING date_from, date_to;
-- end
-- $$;