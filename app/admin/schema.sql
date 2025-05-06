DROP TABLE IF EXISTS database_users;
DROP TABLE IF EXISTS seller_databases;
DROP TABLE IF EXISTS seller_users;
DROP TABLE IF EXISTS sellers;

CREATE TABLE sellers (
	sid varchar NOT NULL,
	name varchar NULL,
	trade_mark varchar NULL,
	"token" varchar NULL,
    active boolean NOT NULL DEFAULT FALSE,
	CONSTRAINT sellers_pkey PRIMARY KEY (sid)
);

CREATE TABLE seller_users (
    id BIGINT,
    seller_sid VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    tg_chat_id BIGINT,
    receive_sales BOOLEAN NOT NULL DEFAULT FALSE,
    receive_supplies_statuses BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (seller_sid) REFERENCES sellers(sid),
    CONSTRAINT seller_users_pkey PRIMARY KEY (id, seller_sid)
);

CREATE TABLE seller_databases (
    host VARCHAR NOT NULL,
    port INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    seller_sid VARCHAR NOT NULL,
    database_type VARCHAR NOT NULL,
    FOREIGN KEY (seller_sid) REFERENCES sellers(sid)
);

CREATE TABLE database_users (
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    seller_sid VARCHAR NOT NULL,
    database_type VARCHAR NOT NULL,
    FOREIGN KEY (seller_sid) REFERENCES sellers(sid),
    CONSTRAINT unique_seller_dbtype UNIQUE (seller_sid, database_type)
);