SET SCHEMA 'vision_data';

CREATE OR REPLACE FUNCTION INSERT_NODE_KEY(_creation_date DATE)
RETURNS UUID AS $$
DECLARE
    new_key_value UUID;
BEGIN
    SET SCHEMA 'vision_data';
    INSERT INTO nodekeys(node_id, creation_date)
    VALUES (NULL, _creation_date)
    RETURNING key_value INTO new_key_value;
    
    RETURN new_key_value;
END;
$$ LANGUAGE plpgsql;

