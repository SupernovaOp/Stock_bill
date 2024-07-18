import sqlite3
from tkinter import *
from tkinter import messagebox

# Initialize Database
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
                        FOREIGN KEY (product_id) REFERENCES products(id))''')
    conn.commit()
    conn.close()

# Add Product
def add_product():
    name = entry_name.get()
    quantity = int(entry_quantity.get())
    price = float(entry_price.get())
    
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Success", "Product added successfully!")
    entry_name.delete(0, END)
    entry_quantity.delete(0, END)
    entry_price.delete(0, END)

# Delete Product
def delete_product():
    product_id = int(entry_delete_id.get())
    
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    
    messagebox.showinfo("Success", "Product deleted successfully!")
    entry_delete_id.delete(0, END)

# Sell Product
def sell_product():
    customer_name = entry_customer_name.get()
    gstin = entry_gstin.get()
    product_id = int(entry_product_id.get())
    quantity = int(entry_sell_quantity.get())
    
    conn = sqlite3.connect('dairy_management.db')
    cursor = conn.cursor()
    cursor.execute("SELECT quantity, price FROM products WHERE id = ?", (product_id,))
    result = cursor.fetchone()
    
    if result and result[0] >= quantity:
        total_price = quantity * result[1]
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
        cursor.execute("INSERT INTO sales (customer_name, gstin, product_id, quantity, total_price) VALUES (?, ?, ?, ?, ?)",
                       (customer_name, gstin, product_id, quantity, total_price))
        conn.commit()
        messagebox.showinfo("Success", f"Product sold successfully! Total Price: {total_price}")
    else:
        messagebox.showerror("Error", "Insufficient stock or invalid product ID.")
    
    conn.close()
    entry_customer_name.delete(0, END)
    entry_gstin.delete(0, END)
    entry_product_id.delete(0, END)
    entry_sell_quantity.delete(0, END)

# Initialize GUI
root = Tk()
root.title("Dairy Product Management")

# Add Product Section
Label(root, text="Add Product").grid(row=0, column=0, columnspan=2)
Label(root, text="Name:").grid(row=1, column=0)
entry_name = Entry(root)
entry_name.grid(row=1, column=1)
Label(root, text="Quantity:").grid(row=2, column=0)
entry_quantity = Entry(root)
entry_quantity.grid(row=2, column=1)
Label(root, text="Price:").grid(row=3, column=0)
entry_price = Entry(root)
entry_price.grid(row=3, column=1)
Button(root, text="Add Product", command=add_product).grid(row=4, column=0, columnspan=2)

# Delete Product Section
Label(root, text="Delete Product").grid(row=5, column=0, columnspan=2)
Label(root, text="Product ID:").grid(row=6, column=0)
entry_delete_id = Entry(root)
entry_delete_id.grid(row=6, column=1)
Button(root, text="Delete Product", command=delete_product).grid(row=7, column=0, columnspan=2)

# Sell Product Section
Label(root, text="Sell Product").grid(row=8, column=0, columnspan=2)
Label(root, text="Customer Name:").grid(row=9, column=0)
entry_customer_name = Entry(root)
entry_customer_name.grid(row=9, column=1)
Label(root, text="GSTIN:").grid(row=10, column=0)
entry_gstin = Entry(root)
entry_gstin.grid(row=10, column=1)
Label(root, text="Product ID:").grid(row=11, column=0)
entry_product_id = Entry(root)
entry_product_id.grid(row=11, column=1)
Label(root, text="Quantity:").grid(row=12, column=0)
entry_sell_quantity = Entry(root)
entry_sell_quantity.grid(row=12, column=1)
Button(root, text="Sell Product", command=sell_product).grid(row=13, column=0, columnspan=2)

initialize_db()
root.mainloop()
