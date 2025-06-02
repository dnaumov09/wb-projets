CREATE TABLE IF NOT EXISTS clusters (
    advert_id UInt32,
    name String,
    count Nullable(UInt32)
)
ENGINE = MergeTree()
ORDER BY name;


CREATE TABLE IF NOT EXISTS keywords (
    advert_id UInt32,
    cluster String,
    keyword String
) 
ENGINE = MergeTree()
ORDER BY keyword;


CREATE TABLE IF NOT EXISTS keywords_stat (
    advert_id UInt32,
    date Date,
    keyword String,
    views UInt32,
    clicks UInt32,
    ctr Float32,
    sum Float64,
    hour Int8
) 
ENGINE = ReplacingMergeTree()
PARTITION BY (date)
ORDER BY (advert_id, date, keyword);


CREATE TABLE IF NOT EXISTS excluded (
    advert_id UInt32,
    keyword String
) 
ENGINE = MergeTree()
ORDER BY keyword;

CREATE TABLE IF NOT EXISTS adverts (
    advert_id UInt32,
    seller_id UInt32,
    create_time DateTime64(3),
    start_time DateTime64(3),
    end_time DateTime64(3),
    change_time DateTime64(3),
    name String,
    daily_budget Float32,
    search_pluse_state Boolean,
    advert_type Int8,
    status Int8,
    payment_type String
)
ENGINE = MergeTree()
ORDER BY advert_id;


CREATE TABLE IF NOT EXISTS adverts_stat (
    advert_id UInt32,
    date Date,
    nm_id UInt32,
    sum Float32,
    views UInt32,
    clicks UInt32,
    atbs UInt32,
    orders UInt32,
    shks UInt32,
    sum_price Float32,
    app_type Int8
) 
ENGINE = ReplacingMergeTree()
ORDER BY (advert_id, date, nm_id, app_type);


CREATE TABLE IF NOT EXISTS adverts_stat_hourly (
    advert_id UInt32,
    date Date,
    nm_id UInt32,
    sum Float32,
    views UInt32,
    clicks UInt32,
    atbs UInt32,
    orders UInt32,
    shks UInt32,
    sum_price Float32,
    app_type Int8,
    hour Int8
) 
ENGINE = ReplacingMergeTree()
ORDER BY (advert_id, date, hour, nm_id, app_type);


CREATE TABLE IF NOT EXISTS cards_stat_hourly (
    nm_id UInt32,
    date Date,
    hour Int8,
    open_card_count UInt32,
    add_to_cart_count UInt32,
    orders_count UInt32,
    orders_sum_rub Float32,
    buyouts_count UInt32,
    buyouts_sum_rub UInt32,
    cancel_count UInt32,
    cancel_sum_rub Float32
) 
ENGINE = ReplacingMergeTree()
ORDER BY (nm_id, date, hour);


CREATE TABLE remains_forecast (
    warehouse_id UInt32,
    nm_id UInt32,
    quantity UInt32,
    last_week_sales_count UInt32,
    avg_daily_sales Float32,
    needed_quantity Float32,
    days_until_stockout Float32,
    reorder_needed Boolean,
    reorder_quantity Float32
)
ENGINE = MergeTree()
ORDER BY (warehouse_id, nm_id);