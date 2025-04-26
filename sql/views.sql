DROP VIEW public.financial_report;
CREATE OR REPLACE VIEW public.financial_report
AS SELECT 
	r.rr_dt,
	r.realizationreport_id,
    r.date_from,
    r.date_to,
    r.create_dt,
    r.gi_id,
    r.nm_id,
    r.doc_type_name,
        CASE
            WHEN r.doc_type_name::text = 'Продажа'::text THEN sum(r.retail_price)
            ELSE - sum(r.retail_price)
        END AS retail_price,
        CASE
            WHEN r.doc_type_name::text = 'Продажа'::text THEN sum(r.retail_amount)
            ELSE - sum(r.retail_amount)
        END AS retail_amount,
    avg(r.sale_percent) AS sale_percent,
        CASE
            WHEN r.doc_type_name::text = 'Продажа'::text THEN sum(r.ppvz_for_pay)
            ELSE - sum(r.ppvz_for_pay)
        END AS ppvz_for_pay,
    sum(r.delivery_rub) AS delivery_rub,
    sum(r.penalty) AS penalty,
    sum(r.additional_payment) AS additional_payment,
    sum(r.storage_fee) AS storage_fee,
    sum(r.acceptance) AS acceptance,
    sum(r.deduction) AS deduction,
        CASE
            WHEN r.doc_type_name::text = 'Продажа'::text THEN sum(r.ppvz_for_pay) - sum(r.delivery_rub) - sum(r.penalty) - sum(r.additional_payment) - sum(r.storage_fee) - sum(r.acceptance) - sum(r.deduction)
            ELSE (- sum(r.ppvz_for_pay)) - sum(r.delivery_rub) - sum(r.penalty) - sum(r.additional_payment) - sum(r.storage_fee) - sum(r.acceptance) - sum(r.deduction)
        END AS ttl_for_pay,
        CASE
            WHEN r.doc_type_name::text = 'Продажа'::text THEN sum(i.buying_price)
            WHEN r.doc_type_name::text = 'Возврат'::text THEN - sum(i.buying_price)
            ELSE 0
        END AS buying_price
   FROM realizations r
  LEFT JOIN incomes i on i.income_id = r.gi_id and i.nm_id = r.nm_id
  GROUP BY r.rr_dt, 
  r.gi_id, i.buying_price,
  r.realizationreport_id, r.create_dt, r.date_from, r.date_to, r.nm_id, r.doc_type_name
  ORDER BY r.rr_dt;


  -- если работает не корректно, то удалить r.gi_id в селекте и r.gi_id, i.buying_price в групбай