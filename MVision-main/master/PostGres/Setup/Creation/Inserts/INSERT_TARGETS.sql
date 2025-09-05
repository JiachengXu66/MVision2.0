SET SCHEMA 'vision_data';
CREATE OR REPLACE FUNCTION INSERT_TARGETS(
    _target_name VARCHAR,
    _alt_name VARCHAR,
    _creation_date DATE,
    _status_value VARCHAR,
    _access VARCHAR,
    _dob DATE,
    _role VARCHAR
)
RETURNS INT AS $$
DECLARE
    new_target_id INT;
BEGIN
    SET SCHEMA 'vision_data';
    INSERT INTO targets(target_name, alt_name, creation_date, status_value, access, dob, role)
    VALUES (_target_name, _alt_name, _creation_date, _status_value, _access, _dob, _role)
    RETURNING target_id INTO new_target_id;
    
    RETURN new_target_id;
END;
$$ LANGUAGE plpgsql;
