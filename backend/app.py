from flask import Flask, jsonify
import psycopg2
from flask_cors import CORS
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)


DB_CONFIG = {
    'dbname': 'retail_data_warehouse',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    """
    Establish a database connection with error handling
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None


QUERIES = {
    "Monthly Sales": """
        SELECT EXTRACT(MONTH FROM sale_date) AS month, 
               ROUND(SUM(revenue), 2) AS total_sales
        FROM retail_sales_fact
        GROUP BY month
        ORDER BY month;
    """,
    "Regional Sales": """
        SELECT locations.region, 
               ROUND(SUM(revenue), 2) AS total_sales
        FROM retail_sales_fact
        JOIN locations ON retail_sales_fact.location_id = locations.location_id
        GROUP BY locations.region
        ORDER BY total_sales DESC;
    """,
    "Top Selling Products": """
        SELECT products.name, 
               SUM(retail_sales_fact.quantity_sold) AS total_sold
        FROM retail_sales_fact
        JOIN products ON retail_sales_fact.product_id = products.product_id
        GROUP BY products.name
        ORDER BY total_sold DESC LIMIT 10;
    """,
    "Employee Sales Performance": """
        SELECT employees.name, 
               ROUND(SUM(retail_sales_fact.revenue), 2) AS total_sales
        FROM retail_sales_fact
        JOIN employees ON retail_sales_fact.employee_id = employees.employee_id
        GROUP BY employees.name
        ORDER BY total_sales DESC;
    """,
    "Sales by Product Category": """
        SELECT products.category, 
               ROUND(SUM(retail_sales_fact.revenue), 2) AS total_sales
        FROM retail_sales_fact
        JOIN products ON retail_sales_fact.product_id = products.product_id
        GROUP BY products.category
        ORDER BY total_sales DESC;
    """,
    "Customer Sales Count": """
        SELECT customers.name, 
               COUNT(retail_sales_fact.sale_id) AS total_sales
        FROM retail_sales_fact
        JOIN customers ON retail_sales_fact.customer_id = customers.customer_id
        GROUP BY customers.name
        ORDER BY total_sales DESC LIMIT 10;
    """,
    "Monthly Revenue Per Product": """
        SELECT EXTRACT(MONTH FROM sale_date) AS month, 
               products.name, 
               ROUND(SUM(retail_sales_fact.revenue), 2) AS total_revenue
        FROM retail_sales_fact
        JOIN products ON retail_sales_fact.product_id = products.product_id
        GROUP BY month, products.name
        ORDER BY month, total_revenue DESC;
    """,
    "Average Sale Value": """
        SELECT ROUND(AVG(revenue), 2) AS average_sale_value
        FROM retail_sales_fact;
    """,
    "Sales By Location": """
        SELECT locations.city, 
               ROUND(SUM(retail_sales_fact.revenue), 2) AS total_sales
        FROM retail_sales_fact
        JOIN locations ON retail_sales_fact.location_id = locations.location_id
        GROUP BY locations.city
        ORDER BY total_sales DESC;
    """,
    "Sales By Customer": """
        SELECT customers.name, 
               ROUND(SUM(retail_sales_fact.revenue), 2) AS total_sales
        FROM retail_sales_fact
        JOIN customers ON retail_sales_fact.customer_id = customers.customer_id
        GROUP BY customers.name
        ORDER BY total_sales DESC;
    """,
    "Product Sales Over Time": """
        SELECT products.name, 
               sale_date, 
               ROUND(SUM(retail_sales_fact.revenue), 2) AS daily_revenue
        FROM retail_sales_fact
        JOIN products ON retail_sales_fact.product_id = products.product_id
        GROUP BY products.name, sale_date
        ORDER BY sale_date;
    """,
    "Top Revenue by Location": """
        SELECT locations.city, 
               ROUND(SUM(retail_sales_fact.revenue), 2) AS total_sales
        FROM retail_sales_fact
        JOIN locations ON retail_sales_fact.location_id = locations.location_id
        GROUP BY locations.city
        ORDER BY total_sales DESC LIMIT 5;
    """,
    "Quarterly Revenue": """
        SELECT EXTRACT(QUARTER FROM sale_date) AS quarter, 
               ROUND(SUM(revenue), 2) AS total_revenue
        FROM retail_sales_fact
        GROUP BY quarter
        ORDER BY quarter;
    """,
    "Yearly Revenue": """
        SELECT EXTRACT(YEAR FROM sale_date) AS year, 
               ROUND(SUM(revenue), 2) AS total_revenue
        FROM retail_sales_fact
        GROUP BY year
        ORDER BY year;
    """,
}

def execute_query(query):
   
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Query execution error: {e}")
        return None
    finally:
        conn.close()

@app.route("/query/<query_name>")
def get_query_data(query_name):
  
    query = QUERIES.get(query_name)
    if not query:
        return jsonify({"error": "Query not found"}), 404
    
    data = execute_query(query)
    if data is None:
        return jsonify({"error": "Failed to fetch data"}), 500
    
    return jsonify(data)

@app.route("/chart/<query_name>")
def get_chart_data(query_name):
   
    query = QUERIES.get(query_name)
    if not query:
        return jsonify({"error": "Query not found"}), 404
    
    data = execute_query(query)
    if not data:
        return jsonify({"error": "Failed to fetch chart data"}), 500
    
    try:
        
        if query_name == "Regional Sales":
            labels = [row.get('region', 'Unknown') for row in data]
            values = [float(row.get('total_sales', 0)) for row in data]
        elif query_name == "Monthly Sales":
            labels = [str(int(row.get('month', 0))) for row in data]
            values = [float(row.get('total_sales', 0)) for row in data]
        else:
           
            first_key = list(data[0].keys())[0]
            labels = [str(row.get(first_key, 'N/A')) for row in data]
            values = [float(list(row.values())[1]) for row in data]
        
        return jsonify({"labels": labels, "values": values})
    
    except (KeyError, IndexError, ValueError) as e:
        return jsonify({"error": f"Data processing error: {str(e)}"}), 500

@app.route("/")
def sales_dashboard():
   
    return "Welcome to the Retail Sales Dashboard!"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
