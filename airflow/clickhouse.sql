CREATE TABLE user_reports (
    user_id String,
    prosthesis_id String,
    total_movements UInt32,
    avg_signal Float32,
    last_activity DateTime,
    report_date Date
)
ENGINE = MergeTree
ORDER BY (user_id, report_date);