# Dashboard Báo cáo Bán hàng

Đây là một ứng dụng web Flask hiển thị các báo cáo bán hàng tương tác dựa trên dữ liệu mẫu được cung cấp.

## Cấu trúc Thư mục

```
sales_dashboard/
├── src/
│   ├── models/          # (Không sử dụng trong phiên bản SQLite này)
│   ├── routes/          # (Các route được định nghĩa trong main.py)
│   ├── static/          # (CSS, JS, Hình ảnh - nếu có)
│   ├── templates/
│   │   ├── index.html
│   │   ├── report_view.html
│   │   └── report_view_with_filter.html
│   └── main.py          # File chạy chính của ứng dụng Flask
├── venv/                # Môi trường ảo Python
├── requirements.txt     # Các thư viện Python cần thiết
├── sales_dashboard.db   # Cơ sở dữ liệu SQLite chứa dữ liệu mẫu
├── schema.sql           # Lược đồ SQL để tạo bảng (đã được dùng để tạo sales_dashboard.db)
└── setup_sqlite.py      # Script Python để tạo CSDL SQLite và nạp dữ liệu từ CSV
```

## Yêu cầu

*   Python 3.x
*   Flask và các thư viện trong `requirements.txt`

## Cách chạy cục bộ

1.  **Giải nén tệp `sales_dashboard_project.zip` (nếu bạn nhận được dưới dạng zip).**

2.  **Mở terminal hoặc command prompt, di chuyển vào thư mục `sales_dashboard`:**
    ```bash
    cd path/to/sales_dashboard
    ```

3.  **(Khuyến nghị) Tạo và kích hoạt môi trường ảo:**
    *   Nếu bạn chưa có `venv`:
        ```bash
        python3 -m venv venv
        ```
    *   Kích hoạt môi trường ảo:
        *   Trên macOS và Linux:
            ```bash
            source venv/bin/activate
            ```
        *   Trên Windows:
            ```bash
            .\venv\Scripts\activate
            ```

4.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    ```
    *Lưu ý: Tệp `requirements.txt` đã được cung cấp trong thư mục `sales_dashboard` của file zip.* 
    *Nếu bạn không có file `requirements.txt` sẵn, nội dung của nó là:
    ```
    Flask==3.0.0
    # (Thêm các thư viện khác nếu có, ví dụ: Jinja2, Werkzeug, itsdangerous, click, blinker thường đi kèm Flask)
    # SQLite3 là một phần của thư viện chuẩn Python, không cần cài đặt riêng qua pip.
    ```
    *Trong trường hợp này, bạn có thể chỉ cần `pip install Flask` nếu `requirements.txt` không đầy đủ hoặc bị thiếu.* 
    *Tuy nhiên, các thư viện cần thiết đã được cài đặt trong môi trường ảo khi `create_flask_app` được chạy, nên `requirements.txt` từ template đó sẽ đầy đủ.* 

5.  **Đảm bảo tệp cơ sở dữ liệu `sales_dashboard.db` nằm trong thư mục `sales_dashboard`.**
    Tệp này đã được tạo và chứa dữ liệu mẫu.
    Nếu bạn muốn tạo lại từ đầu (không khuyến khích trừ khi cần thiết):
    *   Đảm bảo các tệp CSV (`time_data.csv`, `item_data.csv`, v.v.) nằm trong thư mục `/home/ubuntu` (hoặc điều chỉnh đường dẫn trong `setup_sqlite.py`).
    *   Chạy script `setup_sqlite.py`:
        ```bash
        python setup_sqlite.py
        ```
        *(Lưu ý: Script này được thiết kế để chạy từ thư mục cha của `sales_dashboard` nếu đường dẫn CSV là `/home/ubuntu`. Nếu chạy từ trong `sales_dashboard`, bạn có thể cần điều chỉnh đường dẫn CSV trong script `setup_sqlite.py` thành `../`)*

6.  **Chạy ứng dụng Flask:**
    Di chuyển vào thư mục `src` và chạy `main.py`:
    ```bash
    cd src
    python main.py
    ```
    Hoặc từ thư mục `sales_dashboard`:
    ```bash
    python src/main.py
    ```

7.  **Mở trình duyệt web và truy cập:** `http://127.0.0.1:8080`

## Các Báo cáo có sẵn

Ứng dụng cung cấp các báo cáo sau:

*   Báo cáo 1: Thông tin chi tiết mặt hàng theo cửa hàng
*   Báo cáo 2: Cửa hàng bán sản phẩm cho khách hàng cụ thể (Lọc theo ID Khách hàng)
*   Báo cáo 3: Địa chỉ văn phòng của cửa hàng theo tồn kho sản phẩm (Lọc theo ID Sản phẩm, Ngưỡng số lượng)
*   Báo cáo 4: Nơi ở của khách hàng (Lọc theo ID Khách hàng)
*   Báo cáo 5: Tồn kho sản phẩm theo thành phố (Lọc theo ID Sản phẩm, Tên thành phố)
*   Báo cáo 6: Doanh số bán hàng theo Tháng/Quý/Năm (Lọc theo Khoảng thời gian)
*   Báo cáo 7: Top N sản phẩm bán chạy nhất (Lọc theo N, Khoảng thời gian)
*   Báo cáo 8: Phân tích khách hàng theo loại hình và doanh số (Lọc theo Khoảng thời gian)
*   Báo cáo 9: Hiệu suất bán hàng của cửa hàng (Lọc theo Khoảng thời gian)
*   Báo cáo 10: Tình hình tồn kho theo sản phẩm và cửa hàng (Lọc theo Tên sản phẩm, Tên cửa hàng, Tên thành phố)

## Dữ liệu mẫu

Các tệp CSV chứa dữ liệu mẫu được sử dụng để nạp vào cơ sở dữ liệu SQLite:

*   `time_data.csv`
*   `item_data.csv`
*   `city_data.csv`
*   `customer_data.csv`
*   `store_data.csv`
*   `sales_fact_data.csv`
*   `inventory_fact_data.csv`

## Truy vấn SQL

Tệp `report_queries.sql` chứa các truy vấn SQL được sử dụng cho các báo cáo.

## Phân tích ERD

Tệp `analysis_erd_reports.md` chứa phân tích sơ đồ quan hệ thực thể và các yêu cầu báo cáo ban đầu.

