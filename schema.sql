-- SQL Schema for Sales Dashboard

-- Drop tables if they exist (optional, for clean setup)
DROP TABLE IF EXISTS Inventory_Fact;
DROP TABLE IF EXISTS Sales_Fact;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS store;
DROP TABLE IF EXISTS city;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS time;

-- Time Table
CREATE TABLE time (
    time_key INT PRIMARY KEY COMMENT 'Ví dụ: YYYYMMDD',
    day INT,
    month INT,
    quarter INT,
    year INT
);

-- Item Table (DIM_PRODUCT)
CREATE TABLE item (
    item_key INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Tương ứng với Product_id',
    item_name VARCHAR(255) NOT NULL,
    description TEXT,
    size VARCHAR(50),
    weight DECIMAL(10,2) COMMENT 'Đơn vị: kg',
    price DECIMAL(10,2) COMMENT 'Đơn giá bán'
);

-- City Table (DIM_CITY)
CREATE TABLE city (
    city_key INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Tương ứng với City_id',
    city_name VARCHAR(100) NOT NULL,
    office_address VARCHAR(255) COMMENT 'Địa chỉ văn phòng đại diện của cửa hàng tại thành phố đó',
    state VARCHAR(100) NOT NULL COMMENT 'Tương ứng với States'
);

-- Store Table (DIM_STORE)
CREATE TABLE store (
    store_key INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Tương ứng với Store_id',
    phone_number VARCHAR(20),
);

-- Customer Table (DIM_CUSTOMER)
CREATE TABLE customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Tương ứng với Customer_id',
    customer_name VARCHAR(100) NOT NULL,
    customer_type VARCHAR(50) COMMENT 'Ví dụ: Retail, Wholesale',
    city_key INT COMMENT 'Thành phố nơi khách hàng sinh sống, cần cho Báo cáo 4',
    FOREIGN KEY (city_key) REFERENCES city(city_key)
);

-- Sales_Fact Table (FACT_SALE)
CREATE TABLE Sales_Fact (
    sales_fact_id INT PRIMARY KEY AUTO_INCREMENT,
    time_key INT,
    item_key INT,
    customer_key INT,
    store_key INT,
    units_sold INT NOT NULL,
    total_sold DECIMAL(12,2) NOT NULL COMMENT 'Giá trị bằng units_sold * item.price tại thời điểm bán',
    FOREIGN KEY (time_key) REFERENCES time(time_key),
    FOREIGN KEY (item_key) REFERENCES item(item_key),
    FOREIGN KEY (customer_key) REFERENCES customer(customer_key),
    FOREIGN KEY (store_key) REFERENCES store(store_key)
);

-- Inventory_Fact Table (FACT_INVENTORY)
CREATE TABLE Inventory_Fact (
    inventory_fact_id INT PRIMARY KEY AUTO_INCREMENT,
    time_key INT COMMENT 'Thời điểm ghi nhận tồn kho',
    item_key INT,
    store_key INT,
    quantity INT NOT NULL COMMENT 'Số lượng tồn kho hiện tại, tương ứng với quantity trong ERD',
    quantity_received INT COMMENT 'Số lượng đã nhận trong kỳ',
    quantity_sold INT COMMENT 'Số lượng đã bán trong kỳ',
    FOREIGN KEY (time_key) REFERENCES time(time_key),
    FOREIGN KEY (item_key) REFERENCES item(item_key),
    FOREIGN KEY (store_key) REFERENCES store(store_key)
);



