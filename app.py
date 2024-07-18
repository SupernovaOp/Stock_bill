import sqlite3
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import gradio as gr

# Initialize Database and Update Schema
def initialize_db():
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        price REAL NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        customer_name TEXT NOT NULL,
                        gstin TEXT NOT NULL,
                        product_id INTEGER NOT NULL,
                        quantity INTEGER NOT NULL,
                        total_price REAL NOT NULL,
                        bill_filename TEXT,
                        FOREIGN KEY (product_id) REFERENCES products(id))''')
    conn.commit()
    conn.close()

def update_db_schema():
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(sales)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'bill_filename' not in columns:
        cursor.execute("ALTER TABLE sales ADD COLUMN bill_filename TEXT")
        conn.commit()
        
    conn.close()

# Initialize DB and Update Schema
initialize_db()
update_db_schema()

# Add Product
def add_product(name, quantity, price):
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()
    return "Product added successfully!"

# Delete Product
def delete_product(product_id):
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return "Product deleted successfully!"

# Generate PDF bill
def generate_pdf_bill(bill_content, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.drawString(100, height - 40, "Bill Details")
    y = height - 60
    for line in bill_content.split('\n'):
        c.drawString(100, y, line)
        y -= 20
    c.save()

# Sell Product
def sell_product(customer_name, gstin, product_id, quantity):
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT quantity, price FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    
    if result and result[0] >= quantity:
        total_price = quantity * result[1]
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
        
        # Generate unique filename for bill
        bill_filename = f"{customer_name.replace(' ', '_')}_bill.pdf"
        
        # Save bill details to sales table
        cursor.execute("INSERT INTO sales (customer_name, gstin, product_id, quantity, total_price, bill_filename) VALUES (?, ?, ?, ?, ?, ?)",
                       (customer_name, gstin, product_id, quantity, total_price, bill_filename))
        conn.commit()
        
        # Generate and save PDF bill
        bill = f"Customer: {customer_name}\nGSTIN: {gstin}\nProduct ID: {product_id}\nQuantity: {quantity}\nTotal Price: {total_price}"
        generate_pdf_bill(bill, bill_filename)
        
        return f"{bill}\n\nBill saved as '{bill_filename}'."
    else:
        return "Insufficient stock or invalid product ID."
    
    conn.close()

# View Stock
def view_stock():
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["ID", "Name", "Quantity", "Price"])
    return df

# View Sell History
def view_sell_history():
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales")
    data = cursor.fetchall()
    conn.close()

    # Adjust the number of columns if needed
    df = pd.DataFrame(data, columns=["ID", "Customer Name", "GSTIN", "Product ID", "Quantity", "Total Price", "Bill Filename"])
    return df

# Initialize Gradio Interfaces
add_product_interface = gr.Interface(
    fn=add_product,
    inputs=[
        gr.Textbox(label="Name"),
        gr.Number(label="Quantity"),
        gr.Number(label="Price")
    ],
    outputs="text",
    title="Add Product"
)

delete_product_interface = gr.Interface(
    fn=delete_product,
    inputs=gr.Number(label="Product ID"),
    outputs="text",
    title="Delete Product"
)

sell_product_interface = gr.Interface(
    fn=sell_product,
    inputs=[
        gr.Textbox(label="Customer Name"),
        gr.Textbox(label="GSTIN"),
        gr.Number(label="Product ID"),
        gr.Number(label="Quantity")
    ],
    outputs="text",
    title="Sell Product"
)

view_stock_interface = gr.Interface(
    fn=view_stock,
    inputs=None,
    outputs="dataframe",
    title="View Stock"
)

view_sell_history_interface = gr.Interface(
    fn=view_sell_history,
    inputs=None,
    outputs="dataframe",
    title="View Sell History"
)

# Combine Interfaces
app = gr.TabbedInterface(
    [add_product_interface, delete_product_interface, sell_product_interface, view_stock_interface, view_sell_history_interface],
    ["Add Product", "Delete Product", "Sell Product", "View Stock", "View Sell History"]
)

app.launch(share=True)
