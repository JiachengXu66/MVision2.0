SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_TARGET(_target_id INT)
RETURNS JSONB AS $$
DECLARE
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    WITH target_entry AS (
        SELECT *
        FROM targets
        WHERE target_id = _target_id
    )
    SELECT jsonb_agg(to_jsonb(target_entry.*))
    INTO result_json
    FROM target_entry;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
