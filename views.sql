DROP VIEW IF EXISTS daily_stat;
CREATE OR REPLACE VIEW daily_stat 
 AS
 SELECT
    date_trunc('day', p.begin_date) AS day_start,
    SUM(p.open_card_count) AS open_card_count,
    SUM(p.add_to_cart_count) AS add_to_cart_count,
    SUM(p.orders_count) AS orders_count,
    SUM(p.orders_sum_rub) AS orders_sum_rub,
    SUM(p.buyouts_count) AS buyouts_count,
    SUM(p.buyouts_sum_rub) AS buyouts_sum_rub,
    SUM(p.cancel_count) AS cancel_count,
    SUM(p.cancel_sum_rub) AS cancel_sum_rub
 FROM pipeline p
 GROUP BY date_trunc('day', begin_date)
 ORDER BY day_start;
 

DROP VIEW IF EXISTS daily_stat_detailed;
 CREATE OR REPLACE VIEW daily_stat_detailed
 AS
 SELECT c.title,
    c.vendor_code,
    p.card_nm_id as card_nm_id,
    date_trunc('day', p.begin_date) AS day_start,
    sum(p.open_card_count) AS open_card_count,
    sum(p.add_to_cart_count) AS add_to_cart_count,
    sum(p.orders_count) AS orders_count,
    sum(p.orders_sum_rub) AS orders_sum_rub,
    sum(p.buyouts_count) AS buyouts_count,
    sum(p.buyouts_sum_rub) AS buyouts_sum_rub,
    sum(p.cancel_count) AS cancel_count,
    sum(p.cancel_sum_rub) AS cancel_sum_rub
   FROM pipeline p
     JOIN cards c ON c.nm_id = p.card_nm_id
  GROUP BY c.title, c.vendor_code, p.card_nm_id, date_trunc('day', p.begin_date)
  ORDER BY day_start, c.title, c.vendor_code;


DROP VIEW IF EXISTS weekly_stat;
CREATE OR REPLACE VIEW weekly_stat 
 AS
 SELECT
    date_trunc('week', p.begin_date) AS week_start,
    SUM(p.open_card_count) AS open_card_count,
    SUM(p.add_to_cart_count) AS add_to_cart_count,
    SUM(p.orders_count) AS orders_count,
    SUM(p.orders_sum_rub) AS orders_sum_rub,
    SUM(p.buyouts_count) AS buyouts_count,
    SUM(p.buyouts_sum_rub) AS buyouts_sum_rub,
    SUM(p.cancel_count) AS cancel_count,
    SUM(p.cancel_sum_rub) AS cancel_sum_rub
 FROM pipeline p
 GROUP BY date_trunc('week', begin_date)
 ORDER BY week_start;


DROP VIEW IF EXISTS weekly_stat_detailed;
CREATE OR REPLACE VIEW weekly_stat_detailed
 AS
 SELECT c.title,
    c.vendor_code,
    p.card_nm_id as card_nm_id,
    date_trunc('week', p.begin_date) AS week_start,
    sum(p.open_card_count) AS open_card_count,
    sum(p.add_to_cart_count) AS add_to_cart_count,
    sum(p.orders_count) AS orders_count,
    sum(p.orders_sum_rub) AS orders_sum_rub,
    sum(p.buyouts_count) AS buyouts_count,
    sum(p.buyouts_sum_rub) AS buyouts_sum_rub,
    sum(p.cancel_count) AS cancel_count,
    sum(p.cancel_sum_rub) AS cancel_sum_rub
   FROM pipeline p
     JOIN cards c ON c.nm_id = p.card_nm_id
  GROUP BY c.title, c.vendor_code, p.card_nm_id, date_trunc('week', p.begin_date)
  ORDER BY week_start, c.title, c.vendor_code;


DROP VIEW IF EXISTS monthly_stat;
CREATE OR REPLACE VIEW monthly_stat
 AS
 SELECT date_trunc('month', begin_date) AS month_start,
    sum(open_card_count) AS open_card_count,
    sum(add_to_cart_count) AS add_to_cart_count,
    sum(orders_count) AS orders_count,
    sum(orders_sum_rub) AS orders_sum_rub,
    sum(buyouts_count) AS buyouts_count,
    sum(buyouts_sum_rub) AS buyouts_sum_rub,
    sum(cancel_count) AS cancel_count,
    sum(cancel_sum_rub) AS cancel_sum_rub
   FROM pipeline p
  GROUP BY date_trunc('month', begin_date)
  ORDER BY month_start;


DROP VIEW IF EXISTS monthly_stat_detailed;
CREATE OR REPLACE VIEW public.monthly_stat_detailed
 AS
 SELECT c.title,
    c.vendor_code,
    p.card_nm_id as card_nm_id,
    date_trunc('month', p.begin_date) AS month_start,
    sum(p.open_card_count) AS open_card_count,
    sum(p.add_to_cart_count) AS add_to_cart_count,
    sum(p.orders_count) AS orders_count,
    sum(p.orders_sum_rub) AS orders_sum_rub,
    sum(p.buyouts_count) AS buyouts_count,
    sum(p.buyouts_sum_rub) AS buyouts_sum_rub,
    sum(p.cancel_count) AS cancel_count,
    sum(p.cancel_sum_rub) AS cancel_sum_rub
   FROM pipeline p
     JOIN cards c ON c.nm_id = p.card_nm_id
  GROUP BY c.title, c.vendor_code, p.card_nm_id, date_trunc('month', p.begin_date)
  ORDER BY month_start, c.title, c.vendor_code;