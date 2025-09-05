SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_MODEL(_model_id INT)
RETURNS JSONB AS $$
DECLARE
    result_json JSONB;
BEGIN
    SET SCHEMA 'vision_data';
    WITH model_entry AS (
        SELECT *
        FROM models
        WHERE model_id = _model_id
    )
    SELECT jsonb_agg(to_jsonb(model_entry.*))
    INTO result_json
    FROM model_entry;

    RETURN result_json;
END;
$$ LANGUAGE plpgsql;
