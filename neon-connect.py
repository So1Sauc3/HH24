import os
from psycopg2 import pool
from dotenv import load_dotenv

# Load .env file
load_dotenv()
# Get the connection string from the environment variable
connection_string = 'postgresql://recipes_db_owner:hJQ1gMe3yBKD@ep-hidden-surf-a5lxm629.us-east-2.aws.neon.tech/recipes_db?sslmode=require'
# Create a connection pool
connection_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections in the pool
    10,  # Maximum number of connections in the pool
    connection_string
)
# Check if the pool was created successfully
if connection_pool:
    print("Connection pool created successfully")
# Get a connection from the pool
conn = connection_pool.getconn()



# Create a cursor object
cur = conn.cursor()

# Execute SQL commands to retrieve the current time and version from PostgreSQL
cur.execute('SELECT NOW();')
time = cur.fetchone()[0]

cur.execute('SELECT version();')
version = cur.fetchone()[0]

# INSERT INTO ingredient (public_key, name, common_name, last_updated_at, embedding) VALUES (1, 1, 1, NOW(), NULL);")
# ingredient: id, public_key, name, common_name, last_updated_at, embedding, recipe_ingredients_linkers
# recipe: id, public_key, recipe_name, common_name, recipe_link last_updated_at, embedding, recipe_ingredients_linkers

# Close the cursor and return the connection to the pool
conn.commit()
cur.close()
connection_pool.putconn(conn)
# Close all connections in the pool
connection_pool.closeall()

# Print the results
print('Current time:', time)
print('PostgreSQL version:', version)