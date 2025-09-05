SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_REPORT(_report_id INT)
RETURNS JSONB AS $$
DECLARE
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    WITH report_entry AS (
        SELECT *
        FROM reports
        WHERE report_id = _report_id
    )
    SELECT jsonb_agg(to_jsonb(report_entry.*))
    INTO result_json
    FROM report_entry;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
