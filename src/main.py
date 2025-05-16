import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__, static_folder="static", template_folder="templates")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, "sales_dashboard.db")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def index():
    reports = [
        {"id": "report1", "name": "Báo cáo 1: Thông tin chi tiết mặt hàng theo cửa hàng"},
        {"id": "report2", "name": "Báo cáo 2: Cửa hàng bán sản phẩm cho khách hàng cụ thể"},
        {"id": "report3", "name": "Báo cáo 3: Địa chỉ văn phòng của cửa hàng theo tồn kho sản phẩm"},
        {"id": "report4", "name": "Báo cáo 4: Nơi ở của khách hàng"},
        {"id": "report5", "name": "Báo cáo 5: Tồn kho sản phẩm theo thành phố"},
        {"id": "report6_monthly", "name": "Báo cáo 6: Doanh số bán hàng theo Tháng"},
        {"id": "report6_quarterly", "name": "Báo cáo 6: Doanh số bán hàng theo Quý"},
        {"id": "report6_yearly", "name": "Báo cáo 6: Doanh số bán hàng theo Năm"},
        {"id": "report7", "name": "Báo cáo 7: Top N sản phẩm bán chạy nhất"},
        {"id": "report8", "name": "Báo cáo 8: Phân tích khách hàng theo loại hình và doanh số"},
        {"id": "report9", "name": "Báo cáo 9: Hiệu suất bán hàng của cửa hàng"},
        {"id": "report10", "name": "Báo cáo 10: Tình hình tồn kho theo sản phẩm và cửa hàng"}
    ]
    return render_template("index.html", reports=reports)

# --- Report Routes ---

@app.route("/report/report1")
def report1():
    query = """
        SELECT
            s.store_name AS Ten_Cua_Hang,
            s.phone_number AS So_Dien_Thoai_Cua_Hang,
            c.city_name AS Thanh_Pho,
            c.state AS Bang,
            i.item_name AS Ten_Mat_Hang,
            i.description AS Mo_Ta_Mat_Hang,
            i.size AS Kich_Co,
            i.weight AS Trong_Luong_kg,
            i.price AS Don_Gia
        FROM store s
        JOIN city c ON s.city_key = c.city_key
        JOIN Inventory_Fact inv ON s.store_key = inv.store_key
        JOIN item i ON inv.item_key = i.item_key
        WHERE inv.time_key = (SELECT MAX(sub_inv.time_key) FROM Inventory_Fact sub_inv WHERE sub_inv.store_key = s.store_key AND sub_inv.item_key = i.item_key)
        ORDER BY s.store_name, i.item_name;
    """
    data = query_db(query)
    return render_template("report_view.html", title="Báo cáo 1: Thông tin chi tiết mặt hàng theo cửa hàng", data=data, headers=[key for key in data[0].keys()] if data else [])

@app.route("/report/report2", methods=["GET", "POST"])
def report2():
    customer_id = request.form.get("customer_id", "1") # Default to 1 for example
    if request.method == "POST":
        customer_id = request.form["customer_id"]
    
    query = """
        SELECT DISTINCT
            s.store_name AS Ten_Cua_Hang,
            c.city_name AS Thanh_Pho,
            s.phone_number AS So_Dien_Thoai_Cua_Hang,
            i.item_name AS Mat_Hang_Da_Mua
        FROM Sales_Fact sf
        JOIN store s ON sf.store_key = s.store_key
        JOIN city c ON s.city_key = c.city_key
        JOIN item i ON sf.item_key = i.item_key
        WHERE sf.customer_key = ? 
        ORDER BY s.store_name, i.item_name;
    """
    data = query_db(query, [customer_id])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 2: Cửa hàng bán sản phẩm cho khách hàng cụ thể", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "customer_id", "label": "Customer ID", "value": customer_id}
                           ],
                           form_action=request.path)

@app.route("/report/report3", methods=["GET", "POST"])
def report3():
    item_id = request.form.get("item_id", "1")
    quantity_threshold = request.form.get("quantity_threshold", "50")
    if request.method == "POST":
        item_id = request.form["item_id"]
        quantity_threshold = request.form["quantity_threshold"]

    query = """
        SELECT
            s.store_name AS Ten_Cua_Hang,
            c.office_address AS Dia_Chi_Van_Phong,
            c.city_name AS Thanh_Pho,
            c.state AS Bang,
            inv.quantity_on_hand AS So_Luong_Ton_Kho
        FROM Inventory_Fact inv
        JOIN store s ON inv.store_key = s.store_key
        JOIN city c ON s.city_key = c.city_key
        WHERE inv.item_key = ? 
          AND inv.quantity_on_hand > ? 
          AND inv.time_key = (SELECT MAX(sub_inv.time_key) FROM Inventory_Fact sub_inv WHERE sub_inv.store_key = s.store_key AND sub_inv.item_key = inv.item_key)
        ORDER BY c.state, c.city_name, s.store_name;
    """
    data = query_db(query, [item_id, quantity_threshold])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 3: Địa chỉ văn phòng của cửa hàng theo tồn kho sản phẩm", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "item_id", "label": "Item ID", "value": item_id},
                               {"name": "quantity_threshold", "label": "Ngưỡng số lượng", "value": quantity_threshold, "type": "number"}
                           ],
                           form_action=request.path)

@app.route("/report/report4", methods=["GET", "POST"])
def report4():
    customer_id = request.form.get("customer_id", "1")
    if request.method == "POST":
        customer_id = request.form["customer_id"]

    query = """
        SELECT
            cust.customer_name AS Ten_Khach_Hang,
            c.city_name AS Thanh_Pho_Cu_Tru,
            c.state AS Bang_Cu_Tru
        FROM customer cust
        JOIN city c ON cust.city_key = c.city_key
        WHERE cust.customer_key = ?;
    """
    data = query_db(query, [customer_id])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 4: Nơi ở của khách hàng", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "customer_id", "label": "Customer ID", "value": customer_id}
                           ],
                           form_action=request.path)

@app.route("/report/report5", methods=["GET", "POST"])
def report5():
    item_id = request.form.get("item_id", "1")
    city_name = request.form.get("city_name", "Los Angeles") # Example default
    if request.method == "POST":
        item_id = request.form["item_id"]
        city_name = request.form["city_name"]

    query = """
        SELECT
            s.store_name AS Ten_Cua_Hang,
            i.item_name AS Ten_Mat_Hang,
            inv.quantity_on_hand AS So_Luong_Ton_Kho
        FROM Inventory_Fact inv
        JOIN item i ON inv.item_key = i.item_key
        JOIN store s ON inv.store_key = s.store_key
        JOIN city c ON s.city_key = c.city_key
        WHERE i.item_key = ? 
          AND c.city_name = ? 
          AND inv.time_key = (SELECT MAX(sub_inv.time_key) FROM Inventory_Fact sub_inv WHERE sub_inv.store_key = s.store_key AND sub_inv.item_key = i.item_key)
        ORDER BY s.store_name;
    """
    data = query_db(query, [item_id, city_name])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 5: Tồn kho sản phẩm theo thành phố", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "item_id", "label": "Item ID", "value": item_id},
                               {"name": "city_name", "label": "Tên thành phố", "value": city_name}
                           ],
                           form_action=request.path)

# Helper for date range filters
def get_date_filters(request):
    # Default to last year if not provided
    today = datetime.date.today()
    start_year = today.year -1
    default_start_date = datetime.date(start_year, 1, 1).strftime("%Y%m%d")
    default_end_date = datetime.date(start_year, 12, 31).strftime("%Y%m%d")

    start_date = request.form.get("start_date", default_start_date)
    end_date = request.form.get("end_date", default_end_date)
    return start_date, end_date

import datetime # Make sure to import datetime

@app.route("/report/report6_monthly", methods=["GET", "POST"])
def report6_monthly():
    start_date, end_date = get_date_filters(request)
    query = """
        SELECT
            t.year AS Nam,
            t.month AS Thang,
            SUM(sf.units_sold) AS Tong_So_Luong_Ban,
            SUM(sf.total_sold) AS Tong_Doanh_So
        FROM Sales_Fact sf
        JOIN time t ON sf.time_key = t.time_key
        WHERE sf.time_key BETWEEN ? AND ?
        GROUP BY t.year, t.month
        ORDER BY t.year, t.month;
    """
    data = query_db(query, [start_date, end_date])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 6: Doanh số bán hàng theo Tháng", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "start_date", "label": "Từ ngày (YYYYMMDD)", "value": start_date},
                               {"name": "end_date", "label": "Đến ngày (YYYYMMDD)", "value": end_date}
                           ],
                           form_action=request.path)

@app.route("/report/report6_quarterly", methods=["GET", "POST"])
def report6_quarterly():
    start_date, end_date = get_date_filters(request)
    query = """
        SELECT
            t.year AS Nam,
            t.quarter AS Quy,
            SUM(sf.units_sold) AS Tong_So_Luong_Ban,
            SUM(sf.total_sold) AS Tong_Doanh_So
        FROM Sales_Fact sf
        JOIN time t ON sf.time_key = t.time_key
        WHERE sf.time_key BETWEEN ? AND ?
        GROUP BY t.year, t.quarter
        ORDER BY t.year, t.quarter;
    """
    data = query_db(query, [start_date, end_date])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 6: Doanh số bán hàng theo Quý", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "start_date", "label": "Từ ngày (YYYYMMDD)", "value": start_date},
                               {"name": "end_date", "label": "Đến ngày (YYYYMMDD)", "value": end_date}
                           ],
                           form_action=request.path)

@app.route("/report/report6_yearly", methods=["GET", "POST"])
def report6_yearly():
    start_date, end_date = get_date_filters(request)
    query = """
        SELECT
            t.year AS Nam,
            SUM(sf.units_sold) AS Tong_So_Luong_Ban,
            SUM(sf.total_sold) AS Tong_Doanh_So
        FROM Sales_Fact sf
        JOIN time t ON sf.time_key = t.time_key
        WHERE sf.time_key BETWEEN ? AND ?
        GROUP BY t.year
        ORDER BY t.year;
    """
    data = query_db(query, [start_date, end_date])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 6: Doanh số bán hàng theo Năm", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "start_date", "label": "Từ ngày (YYYYMMDD)", "value": start_date},
                               {"name": "end_date", "label": "Đến ngày (YYYYMMDD)", "value": end_date}
                           ],
                           form_action=request.path)

@app.route("/report/report7", methods=["GET", "POST"])
def report7():
    n_param = request.form.get("n_param", "10")
    start_date, end_date = get_date_filters(request)
    # criteria = request.form.get("criteria", "total_sold") # For simplicity, hardcoding to total_sold for now
    
    query = """
        SELECT
            i.item_name AS Ten_San_Pham,
            SUM(sf.total_sold) AS Tong_Doanh_So_Ban_Ra,
            SUM(sf.units_sold) AS Tong_So_Luong_Ban_Ra
        FROM Sales_Fact sf
        JOIN item i ON sf.item_key = i.item_key
        JOIN time t ON sf.time_key = t.time_key
        WHERE t.time_key BETWEEN ? AND ?
        GROUP BY i.item_key, i.item_name
        ORDER BY Tong_Doanh_So_Ban_Ra DESC
        LIMIT ?;
    """
    data = query_db(query, [start_date, end_date, n_param])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 7: Top N sản phẩm bán chạy nhất (theo Doanh số)", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "n_param", "label": "Số lượng N", "value": n_param, "type": "number"},
                               {"name": "start_date", "label": "Từ ngày (YYYYMMDD)", "value": start_date},
                               {"name": "end_date", "label": "Đến ngày (YYYYMMDD)", "value": end_date}
                           ],
                           form_action=request.path)

@app.route("/report/report8", methods=["GET", "POST"])
def report8():
    start_date, end_date = get_date_filters(request)
    query = """
        SELECT
            cust.customer_type AS Loai_Khach_Hang,
            COUNT(DISTINCT cust.customer_key) AS So_Luong_Khach_Hang,
            SUM(sf.units_sold) AS Tong_So_Luong_Ban,
            SUM(sf.total_sold) AS Tong_Doanh_So
        FROM Sales_Fact sf
        JOIN customer cust ON sf.customer_key = cust.customer_key
        JOIN time t ON sf.time_key = t.time_key
        WHERE t.time_key BETWEEN ? AND ?
        GROUP BY cust.customer_type
        ORDER BY Tong_Doanh_So DESC;
    """
    data = query_db(query, [start_date, end_date])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 8: Phân tích khách hàng theo loại hình và doanh số", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "start_date", "label": "Từ ngày (YYYYMMDD)", "value": start_date},
                               {"name": "end_date", "label": "Đến ngày (YYYYMMDD)", "value": end_date}
                           ],
                           form_action=request.path)

@app.route("/report/report9", methods=["GET", "POST"])
def report9():
    start_date, end_date = get_date_filters(request)
    query = """
        SELECT
            s.store_name AS Ten_Cua_Hang,
            c.city_name AS Thanh_Pho,
            SUM(sf.units_sold) AS Tong_So_Luong_Ban,
            SUM(sf.total_sold) AS Tong_Doanh_So,
            COUNT(sf.sales_fact_id) AS Tong_So_Giao_Dich_Chi_Tiet -- Each row in Sales_Fact is a line item
        FROM Sales_Fact sf
        JOIN store s ON sf.store_key = s.store_key
        JOIN city c ON s.city_key = c.city_key
        JOIN time t ON sf.time_key = t.time_key
        WHERE t.time_key BETWEEN ? AND ?
        GROUP BY s.store_key, s.store_name, c.city_name
        ORDER BY Tong_Doanh_So DESC;
    """
    data = query_db(query, [start_date, end_date])
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 9: Hiệu suất bán hàng của cửa hàng", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "start_date", "label": "Từ ngày (YYYYMMDD)", "value": start_date},
                               {"name": "end_date", "label": "Đến ngày (YYYYMMDD)", "value": end_date}
                           ],
                           form_action=request.path)

@app.route("/report/report10", methods=["GET", "POST"])
def report10():
    item_name_filter = request.form.get("item_name_filter", "")
    store_name_filter = request.form.get("store_name_filter", "")
    city_name_filter = request.form.get("city_name_filter", "")

    # Build query with optional filters
    base_query = """
        SELECT
            i.item_name AS Ten_San_Pham,
            s.store_name AS Ten_Cua_Hang,
            c.city_name AS Thanh_Pho,
            inv.quantity_on_hand AS So_Luong_Ton_Kho,
            t.full_date AS Ngay_Cap_Nhat_Ton_Kho
        FROM Inventory_Fact inv
        JOIN item i ON inv.item_key = i.item_key
        JOIN store s ON inv.store_key = s.store_key
        JOIN city c ON s.city_key = c.city_key
        JOIN time t ON inv.time_key = t.time_key
        WHERE inv.time_key = (
            SELECT MAX(sub_inv.time_key) 
            FROM Inventory_Fact sub_inv 
            WHERE sub_inv.store_key = s.store_key AND sub_inv.item_key = i.item_key
        )
    """
    conditions = []
    params = []
    if item_name_filter:
        conditions.append("i.item_name LIKE ?")
        params.append(f"%{item_name_filter}%")
    if store_name_filter:
        conditions.append("s.store_name LIKE ?")
        params.append(f"%{store_name_filter}%")
    if city_name_filter:
        conditions.append("c.city_name LIKE ?")
        params.append(f"%{city_name_filter}%")
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += " ORDER BY i.item_name, s.store_name;"
    
    data = query_db(base_query, params)
    return render_template("report_view_with_filter.html", 
                           title="Báo cáo 10: Tình hình tồn kho theo sản phẩm và cửa hàng", 
                           data=data, 
                           headers=[key for key in data[0].keys()] if data else [],
                           filters=[
                               {"name": "item_name_filter", "label": "Tên sản phẩm (lọc)", "value": item_name_filter},
                               {"name": "store_name_filter", "label": "Tên cửa hàng (lọc)", "value": store_name_filter},
                               {"name": "city_name_filter", "label": "Tên thành phố (lọc)", "value": city_name_filter}
                           ],
                           form_action=request.path)


if __name__ == "__main__":
    # IMPORTANT: For deployment, use a production WSGI server like Gunicorn or Waitress.
    # The following is for development only.
    # Ensure the sales_dashboard.db is in the correct path relative to where this script is run from if not absolute.
    app.run(host="0.0.0.0", port=8080, debug=True)

