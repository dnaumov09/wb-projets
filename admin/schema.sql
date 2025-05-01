DROP TABLE IF EXISTS database_users;
DROP TABLE IF EXISTS seller_databases;
DROP TABLE IF EXISTS sellers;

CREATE TABLE sellers (
	sid varchar NOT NULL,
	name varchar NULL,
	trade_mark varchar NULL,
	"token" varchar NULL,
	CONSTRAINT sellers_pkey PRIMARY KEY (sid)
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