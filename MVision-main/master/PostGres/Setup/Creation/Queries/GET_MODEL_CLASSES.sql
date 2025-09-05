SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_MODEL_CLASSES(_model_id INT)
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_build_object('classes', json_agg(class_id))
    INTO result_json
    FROM ModelClasses
    WHERE model_id = _model_id;

    RETURN result_json;
END;
$$;