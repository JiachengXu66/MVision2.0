SET SCHEMA 'vision_data';

COPY Sources FROM '/docker-entrypoint-initdb.d/DataLoading/Sources.csv' DELIMITER ',' CSV HEADER;
COPY Classes FROM '/docker-entrypoint-initdb.d/DataLoading/Classes.csv' DELIMITER ',' CSV HEADER;
COPY ClassSources FROM '/docker-entrypoint-initdb.d/DataLoading/ClassSources.csv' DELIMITER ',' CSV HEADER;
COPY Categories FROM '/docker-entrypoint-initdb.d/DataLoading/Categories.csv' DELIMITER ',' CSV HEADER;
COPY ClassCategories FROM '/docker-entrypoint-initdb.d/DataLoading/ClassCategories.csv' DELIMITER ',' CSV HEADER;
COPY ModelConfiguration FROM '/docker-entrypoint-initdb.d/DataLoading/ModelConfiguration.csv' DELIMITER ',' CSV HEADER;