#!/usr/bin/env python3
import sqlite3
import csv
import os

DATABASE_PATH = "/home/ubuntu/sales_dashboard/sales_dashboard.db"
CSV_DIR = "csv_data"

TABLE_SCHEMAS = {
    "time": """
        CREATE TABLE IF NOT EXISTS time (
            time_key INTEGER PRIMARY KEY,
            day INTEGER,
            month INTEGER,
            quarter INTEGER,
            year INTEGER,
            full_date TEXT
        );
    """,
    "item": """
        CREATE TABLE IF NOT EXISTS item (
            item_key INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            description TEXT,
            size TEXT,
            weight REAL,
            price REAL
        );
    """,
    "city": """
        CREATE TABLE IF NOT EXISTS city (
            city_key INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL,
            office_address TEXT,
            state TEXT NOT NULL
        );
    """,
    "store": """
        CREATE TABLE IF NOT EXISTS store (
            store_key INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT NOT NULL,
            phone_number TEXT,
            city_key INTEGER,
            FOREIGN KEY (city_key) REFERENCES city(city_key)
        );
    """,
    "customer": """
        CREATE TABLE IF NOT EXISTS customer (
            customer_key INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_type TEXT,
            city_key INTEGER,
            FOREIGN KEY (city_key) REFERENCES city(city_key)
        );
    """,
    "Sales_Fact": """
        CREATE TABLE IF NOT EXISTS Sales_Fact (
            sales_fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_key INTEGER,
            item_key INTEGER,
            customer_key INTEGER,
            store_key INTEGER,
            units_sold INTEGER NOT NULL,
            total_sold REAL NOT NULL,
            FOREIGN KEY (time_key) REFERENCES time(time_key),
            FOREIGN KEY (item_key) REFERENCES item(item_key),
            FOREIGN KEY (customer_key) REFERENCES customer(customer_key),
            FOREIGN KEY (store_key) REFERENCES store(store_key)
        );
    """,
    "Inventory_Fact": """
        CREATE TABLE IF NOT EXISTS Inventory_Fact (
            inventory_fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
            time_key INTEGER,
            item_key INTEGER,
            store_key INTEGER,
            quantity_on_hand INTEGER NOT NULL,
            FOREIGN KEY (time_key) REFERENCES time(time_key),
            FOREIGN KEY (item_key) REFERENCES item(item_key),
            FOREIGN KEY (store_key) REFERENCES store(store_key)
        );
    """
}

# Order matters for foreign key constraints if we were enforcing them during creation
# For SQLite, it is generally fine as FKs are often not enforced by default during inserts unless PRAGMA foreign_keys = ON;
TABLE_NAMES_CSV_MAP = [
    ("time", "time_data.csv"),
    ("item", "item_data.csv"),
    ("city", "city_data.csv"),
    # Customer and Store depend on City
    ("customer", "customer_data.csv"),
    ("store", "store_data.csv"),
    # Sales_Fact and Inventory_Fact depend on others
    ("Sales_Fact", "sales_fact_data.csv"),
    ("Inventory_Fact", "inventory_fact_data.csv")
]

def create_tables(conn):
    cursor = conn.cursor()
    # Enable foreign key support if desired for stricter checks, though not strictly necessary for this script to run
    # cursor.execute("PRAGMA foreign_keys = ON;")
    for table_name, schema in TABLE_SCHEMAS.items():
        print(f"Creating table {table_name}...")
        cursor.execute(schema)
    conn.commit()
    print("All tables created.")

def load_csv_data(conn):
    cursor = conn.cursor()
    for table_name, csv_filename in TABLE_NAMES_CSV_MAP:
        csv_path = os.path.join(CSV_DIR, csv_filename)
        if not os.path.exists(csv_path):
            print(f"CSV file {csv_path} not found for table {table_name}. Skipping.")
            continue
        
        print(f"Loading data from {csv_filename} into {table_name}...")
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader) # Skip header row
            num_columns = len(header)
            placeholders = ",".join(["?"] * num_columns)
            insert_sql = f"INSERT INTO {table_name} ({', '.join(header)}) VALUES ({placeholders})"
            
            rows_to_insert = []
            for row in reader:
                # Basic data type conversion based on common patterns, can be improved
                converted_row = []
                for i, value in enumerate(row):
                    # Attempt to convert to int or float if possible, otherwise keep as string
                    try:
                        if "." in value:
                            converted_row.append(float(value))
                        else:
                            converted_row.append(int(value))
                    except ValueError:
                        converted_row.append(value)
                rows_to_insert.append(tuple(converted_row))

            try:
                cursor.executemany(insert_sql, rows_to_insert)
                conn.commit()
                print(f"Successfully loaded {len(rows_to_insert)} rows into {table_name}.")
            except sqlite3.Error as e:
                print(f"Error loading data into {table_name}: {e}")
                print(f"Failed SQL: {insert_sql}")
                if rows_to_insert:
                    print(f"Sample failed row: {rows_to_insert[0]}")
                conn.rollback() # Rollback on error for this table

def main():
    # Ensure the directory for the database exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    print(f"Database created/connected at {DATABASE_PATH}")
    
    create_tables(conn)
    load_csv_data(conn)
    
    conn.close()
    print("SQLite database setup complete.")

if __name__ == "__main__":
    main()

