-- Scoped application user for the Dow project (least privilege).
-- Applied by scripts/init_clickhouse.py with an admin account; ${DOW_CLICKHOUSE_PASSWORD}
-- is substituted from the environment (default: dow_secret).
-- NO DROP, TRUNCATE, RENAME, ATTACH/DETACH, GRANT or SYSTEM: a buggy statement cannot damage
-- other projects. usstock and twstock are read-only.
-- Migrations that EXCHANGE TABLES need ALTER on dow.*: run them with the admin account.

CREATE USER IF NOT EXISTS dow_user IDENTIFIED BY '${DOW_CLICKHOUSE_PASSWORD}';
GRANT SELECT, INSERT, ALTER DELETE, ALTER UPDATE, CREATE TABLE, OPTIMIZE ON dow.* TO dow_user;
GRANT SELECT ON usstock.* TO dow_user;
GRANT SELECT ON twstock.* TO dow_user;
