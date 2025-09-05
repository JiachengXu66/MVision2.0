SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_CATEGORIES_MAP()
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_object_agg(category_id::text, category_name)
    INTO result_json
    FROM categories;

    RETURN result_json;
END;
$$;
