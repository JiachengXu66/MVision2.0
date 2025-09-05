SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_LATEST_REPORTS(_item_limit INT, _current_page INT)
RETURNS JSONB AS $$
DECLARE
    offset_value INT;
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    offset_value := (_current_page - 1) * _item_limit;
    WITH page_entries AS (
        SELECT *
        FROM reports
        ORDER BY report_id DESC
        LIMIT _item_limit OFFSET offset_value
    )
    SELECT jsonb_agg(to_jsonb(page_entries))
    INTO result_json
    FROM page_entries;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
