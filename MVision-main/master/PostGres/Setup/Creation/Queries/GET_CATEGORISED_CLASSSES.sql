SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION GET_CATEGORISED_CLASSES() 
RETURNS JSON
LANGUAGE plpgsql
AS $$
DECLARE
    result_json JSON;
BEGIN
    SET SCHEMA 'vision_data';
    SELECT json_object_agg(subquery.category_id::text, subquery.classes)
    INTO result_json
    FROM (
        SELECT category.category_id, json_agg(class_category.class_id) as classes
        FROM Categories category
        JOIN ClassCategories class_category ON category.category_id = class_category.category_id
        GROUP BY category.category_id
    ) AS subquery;

    RETURN result_json;
END;
$$;
