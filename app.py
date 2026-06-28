from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

# ✉️ EMAIL CONFIGURATION (Yahan apni details daalein)
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  
RECEIVER_EMAIL = "receiver_email@gmail.com"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        # 🛒 15+ MEGA SHOPPING DATA LIST
        sample_products = [
            # --- Tech & Electronics ---
            ('Wireless Headphones', 2999.00, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500', 'High-quality sound with active bass boost.'),
            ('Smart Fitness Watch', 4500.00, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500', 'Track your fitness, heart rate, and logs.'),
            ('Premium Smartphone', 69999.00, 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500', 'Flagship camera with crystal clear display.'),
            ('Sleek Ultrabook Laptop', 54999.00, 'https://images.unsplash.com/photo-1496181130204-755241524eab?w=500', 'Lightweight, power-packed device for smooth workflow.'),
            ('4K Action Camera', 12499.00, 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500', 'Capture your adventure loops in ultra high definition.'),
            
            # --- Gaming Setup ---
            ('RGB Gaming Mouse', 1200.00, 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500', 'Ergonomic layout with customizable DPI buttons.'),
            ('Mechanical Keyboard', 3499.00, 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500', 'Tactile clicky switches with dynamic RGB patterns.'),
            ('RGB Gaming Desk Mat', 799.00, 'https://images.unsplash.com/photo-1616440347437-b1c73416efc2?w=500', 'Extremely smooth friction surface with custom neon edges.'),
            
            # --- Fashion & Clothing ---
            ('Oversized Black Hoodie', 1899.00, 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500', 'Super comfortable heavy fleece streetwear wear.'),
            ('White Sports Sneakers', 2499.00, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500', 'Flexible soles engineered for modern aesthetic sports.'),
            ('Classic Dark Sunglasses', 999.00, 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=500', 'UV protected polarized stylish summer outfit.'),
            ('Minimalist Daily Backpack', 2199.00, 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500', 'Water resistant daily compartment safety luggage.'),
            
            # --- Lifestyle & Decor ---
            ('Stainless Water Flask', 649.00, 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500', 'Vacuum insulated hot & cold water thermal setup.'),
            ('Ceramic Coffee Mug', 499.00, 'https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=500', 'Matte finish textured insulation container cup.'),
            ('Aromatic Scented Candle', 399.00, 'https://images.unsplash.com/photo-1603006905003-be475563bc59?w=500', 'Lavender extracts to calm your workspace setup.')
        ]
        cursor.executemany('INSERT INTO products (name, price, image, description) VALUES (?, ?, ?, ?)', sample_products)
        conn.commit()
    conn.close()

def send_order_email(customer_name, customer_email, customer_phone, cart_items, total_amount):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = f"🚀 New Order Placed by {customer_name}"

        items_text = ""
        for item in cart_items:
            items_text += f"- {item['name']} (Qty: {item['quantity']}) - ₹{item['price'] * item['quantity']}\n"

        body = f"""
        Hello Admin,
        
        A new order has been received on NeoShop!
        
        👤 Customer Info:
        Name: {customer_name}
        Email: {customer_email}
        Phone: {customer_phone}
        
        🛒 Order Summary:
        {items_text}
        
        💰 Total Collected Amount: ₹{total_amount:.2f}
        
        Regards,
        NeoShop Core System
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Email transmission warning:", e)
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    cart = data.get('cart', [])
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    if not cart:
        return jsonify({'error': 'Cart is empty!'}), 400
    if not name or not email or not phone:
        return jsonify({'error': 'Fields are mandatory!'}), 400

    total_amount = sum(item['price'] * item['quantity'] for item in cart)
    email_sent = send_order_email(name, email, phone, cart, total_amount)

    return jsonify({
        'message': 'Order successfully transmitted via network!',
        'email_status': 'Dispatched' if email_sent else 'Local validation successful (Email skipped)',
        'total_amount': total_amount
    }), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
