DROP VIEW public.financial_report;
CREATE OR REPLACE VIEW public.financial_report
AS SELECT 
	rr_dt,
	realizationreport_id,
    date_from,
    date_to,
    create_dt,
    nm_id,
    doc_type_name,
        CASE
            WHEN doc_type_name::text = 'Продажа'::text THEN sum(retail_price)
            ELSE - sum(retail_price)
        END AS retail_price,
        CASE
            WHEN doc_type_name::text = 'Продажа'::text THEN sum(retail_amount)
            ELSE - sum(retail_amount)
        END AS retail_amount,
    avg(sale_percent) AS sale_percent,
        CASE
            WHEN doc_type_name::text = 'Продажа'::text THEN sum(ppvz_for_pay)
            ELSE - sum(ppvz_for_pay)
        END AS ppvz_for_pay,
    sum(delivery_rub) AS delivery_rub,
    sum(penalty) AS penalty,
    sum(additional_payment) AS additional_payment,
    sum(storage_fee) AS storage_fee,
    sum(acceptance) AS acceptance,
    sum(deduction) AS deduction,
        CASE
            WHEN doc_type_name::text = 'Продажа'::text THEN sum(ppvz_for_pay) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction)
            ELSE (- sum(ppvz_for_pay)) - sum(delivery_rub) - sum(penalty) - sum(additional_payment) - sum(storage_fee) - sum(acceptance) - sum(deduction)
        END AS ttl_for_pay
   FROM realizations r
  GROUP BY rr_dt, realizationreport_id, create_dt, date_from, date_to, nm_id, doc_type_name
  ORDER BY rr_dt;