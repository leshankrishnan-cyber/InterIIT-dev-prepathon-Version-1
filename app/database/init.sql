CREATE TABLE IF NOT EXISTS constants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    symbol VARCHAR(20),
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    description TEXT
);

INSERT INTO constants (name, symbol, value, unit, description)
VALUES
    ('pi', 'π', 3.141592653589793, 'dimensionless', 'Pi'),
    ('e', 'e', 2.718281828459045, 'dimensionless', 'Euler''s number'),
    ('speed_of_light', 'c', 299792458, 'm/s', 'Speed of light in vacuum'),
    ('gravity', 'g', 9.80665, 'm/s²', 'Standard gravitational acceleration')
ON CONFLICT (name) DO NOTHING;
