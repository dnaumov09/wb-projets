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

CREATE OR REPLACE FUNCTION get_sales_by_period(
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
    for_pay double precision, 
    avg_for_pay double precision, 
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
            sum(for_pay),
            avg(for_pay),
            sum(finished_price),
            avg(finished_price),
            sum(price_with_disc),
            avg(price_with_disc)
        FROM sales
        WHERE price_with_disc >= 0
        GROUP BY period, nm_id
        ORDER BY period, nm_id',
        period_type
    );
END;
$$;


DROP FUNCTION IF EXISTS get_pipeline_by_period(text);

CREATE OR REPLACE FUNCTION get_pipeline_by_period(
    period_type text
)
RETURNS TABLE (
    period TIMESTAMP,
    nm_id INT,
    open_card_count BIGINT,
    add_to_cart_count BIGINT,
    orders_count BIGINT,
    orders_sum DOUBLE PRECISION,
    sales_count BIGINT,
    sales_sum DOUBLE PRECISION,
    orders_cancelled_count BIGINT,
    orders_cancelled_sum DOUBLE PRECISION
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Validate period_type
    IF period_type NOT IN ('day', 'week', 'month') THEN
        RAISE EXCEPTION 'Invalid period_type: %, allowed values are day, week, month', period_type;
    END IF;

    -- Main query with COALESCE to handle NULLS
    RETURN QUERY EXECUTE format(
        'SELECT 
            cs.period,
            cs.nm_id,
            cs.open_card_count,
            cs.add_to_cart_count,
            COALESCE(o.count, 0) as orders_count,
            COALESCE(o.price_with_disc, 0) as orders_sum,
            COALESCE(s.count, 0) as sales_count,
            COALESCE(s.price_with_disc, 0) as sales_sum,
            COALESCE(oc.count, 0) as orders_cancelled_count,
            COALESCE(oc.price_with_disc, 0) as orders_cancelled_sum
        FROM get_cards_stat_by_period(%L) cs
        LEFT JOIN get_orders_by_period(%L) o ON o.nm_id = cs.nm_id AND o.period = cs.period
        LEFT JOIN get_sales_by_period(%L) s ON s.nm_id = cs.nm_id AND s.period = cs.period
        LEFT JOIN get_orders_cancelled_by_period(%L) oc ON oc.nm_id = cs.nm_id AND oc.period = cs.period',
        period_type, period_type, period_type, period_type
    );
END;
$$;


CREATE OR REPLACE VIEW financial_report
AS SELECT realizationreport_id, -- ID отчета
    date_from, -- От
    date_to, -- До
    create_dt, -- Дата создания отчета
    doc_type_name, -- Тип документа ("Продажа", "Возврат", " ")
    sum(retail_price) AS retail_price, -- Цена розничная
    sum(retail_amount) AS retail_amount, -- Вайлдберриз реализовал Товар (Пр)
    avg(sale_percent) AS sale_percent, -- Согласованная скидка, %
    sum(ppvz_for_pay) AS ppvz_for_pay, -- К перечислению за товар
    sum(delivery_rub) AS delivery_rub, -- Стоимость логистики
    sum(penalty) AS penalty, -- Общая сумма штрафов
    sum(additional_payment) AS additional_payment, -- Доплаты
    sum(storage_fee) AS storage_fee, -- Стоимость хранения
    sum(acceptance) AS acceptance, -- Стоимость платной приемки
    sum(deduction) AS deduction, -- Прочие удержания/выплаты
        CASE
            WHEN doc_type_name = 'Возврат'
            THEN sum(ppvz_for_pay) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction) - sum(retail_amount) * 2
            ELSE sum(ppvz_for_pay) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction)
        END AS ttl_for_pay -- Итого к оплате,
    sum(retail_price) * 0.07 AS vat7, -- Налог, 7% от розничной цены
        CASE
            WHEN doc_type_name = 'Возврат'
            THEN sum(ppvz_for_pay) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction) - sum(retail_price) * 0.07 - sum(retail_amount) * 2
            ELSE sum(ppvz_for_pay) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction) - sum(retail_price) * 0.07
        END AS after_vat7  -- Прибыль после налогов, 7%
   FROM realizations r
  GROUP BY realizationreport_id, create_dt, date_from, date_to, doc_type_name
  ORDER BY create_dt DESC;


DROP FUNCTION get_financial_report_by_period(text);
CREATE OR REPLACE FUNCTION get_financial_report_by_period(
    period_type text
)
RETURNS TABLE (
    date_from TIMESTAMP,
    date_to TIMESTAMP,
    retail_price double precision,
    retail_amount double precision,
    sale_percent double precision,
    ppvz_for_pay double precision,
    delivery_rub double precision,
    penalty double precision,
    storage_fee double precision,
    acceptance double precision,
    deduction double precision,
    ttl_for_pay double precision,
    vat7 double precision,
    after_vat7 double precision
)
LANGUAGE plpgsql
AS $$
BEGIN
	RETURN QUERY EXECUTE format(
		'select 
			min(fr.date_from) as date_from,
			max(fr.date_to) as date_to,
			sum(fr.retail_price) as retail_price,
			sum(fr.retail_amount) as retail_amount,
			sum(fr.ppvz_for_pay) as ppvz_for_pay,
			sum(fr.delivery_rub) as delivery_rub,
			sum(fr.penalty) as penalty,
			sum(fr.additional_payment) as additional_payment,
			sum(fr.storage_fee) as storage_fee,
			sum(fr.acceptance) as acceptance,
			sum(fr.deduction) as deduction,
			sum(fr.ttl_for_pay) as ttl_for_pay,
			sum(fr.vat7) as vat7,
			sum(fr.after_vat7) as after_vat7
		from financial_report fr
		group by 
			date_trunc(%L, fr.date_from)
		order by
			date_from', period_type);
END
$$;