SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_DEPLOYMENT(_deployment_id INT)
RETURNS JSONB AS $$
DECLARE
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    WITH deployment_entry AS (
        SELECT *
        FROM deployments
        WHERE deployment_id = _deployment_id
    )
    SELECT jsonb_agg(to_jsonb(deployment_entry.*))
    INTO result_json
    FROM deployment_entry;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
