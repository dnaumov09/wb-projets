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


DROP VIEW IF EXISTS financial_report;
CREATE OR REPLACE VIEW financial_report AS
SELECT realizationreport_id, -- ID отчета
    date_from, -- От
    date_to, -- До
    create_dt, -- Дата создания отчета
    doc_type_name, --Тип документа
    CASE
    	WHEN doc_type_name = 'Продажа' THEN sum(retail_price)
        ELSE -sum(retail_price)
    END AS retail_price, -- Цена розничная
	CASE
    	WHEN doc_type_name = 'Продажа' THEN sum(retail_amount)
        ELSE -sum(retail_amount)
    END AS retail_amount, -- Вайлдберриз реализовал Товар (Пр)
    avg(sale_percent) AS sale_percent, -- Согласованная скидка, %
    CASE
    	WHEN doc_type_name = 'Продажа' THEN sum(ppvz_for_pay)
        ELSE -sum(ppvz_for_pay)
    END AS ppvz_for_pay, -- К перечислению продавцу за реализованный товар
    
    sum(delivery_rub) AS delivery_rub, -- Услуги по доставке товара покупателю
    sum(penalty) AS penalty, -- Общая сумма штрафов
    sum(additional_payment) AS additional_payment, -- Доплаты
    sum(storage_fee) AS storage_fee, -- Стоимость хранения
    sum(acceptance) AS acceptance, -- Стоимость платной приёмки
    sum(deduction) AS deduction, -- Прочие удержания/выплаты
    CASE
    	WHEN doc_type_name = 'Продажа' THEN 
			sum(ppvz_for_pay) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction)
		ELSE 
			-sum(ppvz_for_pay) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction)
    END AS ttl_for_pay -- Итоговая сумма выплаты
   FROM realizations r
  GROUP BY realizationreport_id, create_dt, date_from, date_to, doc_type_name
  ORDER BY create_dt DESC;


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
			sum(fr.ttl_for_pay) as ttl_for_pay
		from financial_report fr
		group by 
			date_trunc(%L, fr.date_from)
		order by
			date_from', period_type);
END
$$;


drop view if exists financial_report_detailed;
create or replace view financial_report_detailed as
select 
	r.realizationreport_id,
    r.nm_id,
	r.doc_type_name,
	r.supplier_oper_name,
	case
		when r.doc_type_name = 'Продажа' and (
        	r.supplier_oper_name = 'Продажа'
       	)
       	then sum(r.quantity)
       	when r.doc_type_name = 'Продажа' and (
        	r.supplier_oper_name = 'Авансовая оплата за товар без движения'
        	or r.supplier_oper_name = 'Корректная продажа'
        	or r.supplier_oper_name = 'Частичная компенсация брака'
       	)
       	then 1
        when r.doc_type_name = 'Возврат' and (
			r.supplier_oper_name = 'Корректный возврат' 
        	or r.supplier_oper_name = 'Возврат' 
        	or r.supplier_oper_name = 'Авансовая оплата за товар без движения'
        	or r.supplier_oper_name = 'Сторно продаж'
        	or r.supplier_oper_name = 'Компенсация подменного товара'
        )
        then -sum(r.quantity)
        when r.doc_type_name = '' and (
        	r.supplier_oper_name = 'Возмещение издержек по перевозке/по складским операциям с товаром'
        )
        then 0
        when r.doc_type_name = '' and (
        	r.supplier_oper_name = 'Штрафы'
        	or r.supplier_oper_name = 'Логистика'
        	or r.supplier_oper_name = 'Логистика сторно'
        )
        then 0
        when r.doc_type_name = '' and (
        	r.supplier_oper_name = 'Сторно возвратов'
        )
        then 1
    end as quantity, --Количество
    case
    	when r.doc_type_name = 'Возврат' and (
			r.supplier_oper_name = 'Корректный возврат' 
        	or r.supplier_oper_name = 'Возврат' 
        	or r.supplier_oper_name = 'Авансовая оплата за товар без движения'
        	or r.supplier_oper_name = 'Сторно продаж'
        	or r.supplier_oper_name = 'Компенсация подменного товара'
        )
        then -sum(r.retail_amount)
        else sum(r.retail_amount)
    end as retail_amount, -- Вайлдберриз реализовал Товар (Пр)
    case
    	when r.doc_type_name = 'Возврат' and (
			r.supplier_oper_name = 'Корректный возврат' 
        	or r.supplier_oper_name = 'Возврат' 
        	or r.supplier_oper_name = 'Авансовая оплата за товар без движения'
        	or r.supplier_oper_name = 'Сторно продаж'
        	or r.supplier_oper_name = 'Компенсация подменного товара'
        )
        then -sum(r.ppvz_for_pay)
        else sum(r.ppvz_for_pay)
    end as ppvz_for_pay, -- К перечислению продавцу за реализованный товар
    sum(r.penalty) as penalty, -- Общая сумма штрафов
    sum(r.additional_payment) as additional_payment, -- Доплаты,
    sum(storage_fee) as storage_fee, -- Хранение
    sum(delivery_rub) as delivery_rub, -- Логистика
    sum(acceptance) as acceptance, -- Платная приемка
    sum(deduction) as deduction -- Прочие удержания/выплаты
from realizations r
group by r.nm_id, r.doc_type_name, r.supplier_oper_name, r.realizationreport_id
order by r.nm_id;


DROP FUNCTION get_financial_report_by_report_ids(report_ids int4[]);
CREATE OR REPLACE FUNCTION get_financial_report_by_report_ids(report_ids int4[])
 RETURNS TABLE(
 	nm_id int4,
 	quantity double precision,
 	retail_amount double precision,
 	ppvz_for_pay double precision,
 	penalty double precision,
 	additional_payment double precision,
 	delivery_rub double precision,
 	storage_fee double precision,
 	acceptance double precision,
 	deduction double precision
 )
 LANGUAGE plpgsql
AS $$
begin
	RETURN QUERY 
    EXECUTE '
        SELECT 
            nm_id,
            SUM(quantity)::double precision AS quantity,
            SUM(retail_amount)::double precision AS retail_amount,
            SUM(ppvz_for_pay)::double precision AS ppvz_for_pay,
            SUM(penalty)::double precision AS penalty,
            SUM(additional_payment)::double precision AS additional_payment,
            SUM(delivery_rub)::double precision AS delivery_rub,
            SUM(storage_fee)::double precision AS storage_fee,
            SUM(acceptance)::double precision AS acceptance,
            SUM(deduction)::double precision AS deduction
        FROM financial_report_detailed
        WHERE realizationreport_id = ANY($1)
        GROUP BY nm_id
        ORDER BY nm_id'
    USING report_ids;
end
$$;