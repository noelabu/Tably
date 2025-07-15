-- initial addition of columns
ALTER TABLE businesses ADD COLUMN city VARCHAR(255);
ALTER TABLE businesses ADD COLUMN state VARCHAR(255);
ALTER TABLE businesses ADD COLUMN zip_code VARCHAR(255);
ALTER TABLE businesses ADD COLUMN phone VARCHAR(255);
ALTER TABLE businesses ADD COLUMN email VARCHAR(255);
ALTER TABLE businesses ADD COLUMN cuisine_type VARCHAR(255);
ALTER TABLE businesses ADD COLUMN open_time VARCHAR(255);
ALTER TABLE businesses ADD COLUMN close_time VARCHAR(255);

-- alter column types to text
ALTER TABLE businesss ALTER COLUMN city TYPE TEXT;
ALTER TABLE businesss ALTER COLUMN state TYPE TEXT;
ALTER TABLE businesss ALTER COLUMN zip_code TYPE TEXT;
ALTER TABLE businesss ALTER COLUMN phone TYPE TEXT;
ALTER TABLE businesss ALTER COLUMN email TYPE TEXT;
ALTER TABLE businesss ALTER COLUMN cuisine_type TYPE TEXT;
ALTER TABLE businesss ALTER COLUMN open_time TYPE TEXT;
ALTER TABLE businesss ALTER COLUMN close_time TYPE TEXT;
