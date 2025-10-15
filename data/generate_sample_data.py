"""Generate synthetic sample data for testing."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_sample_data(num_orders: int = 500, num_customers: int = 100) -> pd.DataFrame:
    """Generate synthetic Salla order data.
    
    Args:
        num_orders: Number of orders to generate
        num_customers: Number of unique customers
        
    Returns:
        DataFrame with sample order data
    """
    # Date range: last 12 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Generate dates with more recent orders
    dates = []
    for _ in range(num_orders):
        days_ago = int(np.random.exponential(scale=100))
        if days_ago > 365:
            days_ago = 365
        order_date = end_date - timedelta(days=days_ago)
        dates.append(order_date)
    
    # Customer IDs (some customers order multiple times)
    customer_weights = np.random.zipf(1.5, num_customers)
    customer_weights = customer_weights / customer_weights.sum()
    customer_ids = np.random.choice(
        range(1000, 1000 + num_customers),
        size=num_orders,
        p=customer_weights,
        replace=True
    )
    
    # Products
    products = [
        ('Premium Coffee Beans 1kg', 'Food & Beverages', 89.99),
        ('Organic Green Tea Set', 'Food & Beverages', 45.00),
        ('Wireless Bluetooth Headphones', 'Electronics', 199.99),
        ('Smart Watch Series 5', 'Electronics', 899.00),
        ('Yoga Mat Premium', 'Sports & Fitness', 79.99),
        ('Running Shoes Pro', 'Sports & Fitness', 299.00),
        ('Designer Handbag', 'Fashion', 1299.00),
        ('Cotton T-Shirt Pack', 'Fashion', 89.00),
        ('Skincare Gift Set', 'Beauty', 149.99),
        ('Aromatherapy Diffuser', 'Home & Living', 59.99),
        ('Kitchen Knife Set', 'Home & Living', 129.00),
        ('Book: Business Strategy', 'Books', 39.99),
        ('Bluetooth Speaker', 'Electronics', 79.99),
        ('Protein Powder 2kg', 'Food & Beverages', 199.00),
        ('Gaming Mouse RGB', 'Electronics', 149.00),
    ]
    
    # Generate orders
    orders = []
    for i in range(num_orders):
        order_id = f"ORD{10000 + i}"
        customer_id = f"CUST{customer_ids[i]}"
        order_date = dates[i]
        
        # Random number of items per order (1-5)
        num_items = np.random.choice([1, 2, 3, 4, 5], p=[0.5, 0.25, 0.15, 0.07, 0.03])
        
        # Select random products
        order_products = random.sample(products, min(num_items, len(products)))
        
        order_total = 0
        for product_name, category, base_price in order_products:
            # Add some price variation
            price = base_price * np.random.uniform(0.9, 1.1)
            quantity = np.random.choice([1, 2, 3], p=[0.7, 0.2, 0.1])
            unit_price = price
            line_total = price * quantity
            order_total += line_total
            
            # Order status (mostly completed)
            status = np.random.choice(
                ['completed', 'completed', 'completed', 'completed', 'pending', 'cancelled'],
                p=[0.85, 0.05, 0.05, 0.03, 0.01, 0.01]
            )
            
            orders.append({
                'order_id': order_id,
                'order_date': order_date.strftime('%Y-%m-%d'),
                'customer_id': customer_id,
                'customer_name': f"Customer {customer_ids[i]}",
                'customer_email': f"customer{customer_ids[i]}@example.com",
                'customer_phone': f"+966{random.randint(500000000, 599999999)}",
                'product_name': product_name,
                'category': category,
                'quantity': quantity,
                'unit_price': round(unit_price, 2),
                'line_total': round(line_total, 2),
                'order_total': round(order_total, 2),
                'order_status': status,
                'currency': 'SAR',
                'payment_method': np.random.choice(['credit_card', 'debit_card', 'cash_on_delivery'], p=[0.5, 0.3, 0.2]),
                'shipping_city': np.random.choice(['Riyadh', 'Jeddah', 'Dammam', 'Mecca', 'Medina'], p=[0.4, 0.3, 0.15, 0.1, 0.05])
            })
    
    df = pd.DataFrame(orders)
    
    # Add some Arabic headers as synonyms (in comment for reference)
    # Original headers can be in Arabic: رقم_الطلب, تاريخ_الطلب, etc.
    
    return df

def main():
    """Generate and save sample data."""
    print("Generating sample Salla data...")
    
    # Generate data with 20,000 orders to match real Salla exports
    df = generate_sample_data(num_orders=20000, num_customers=500)
    
    # Save to Excel
    output_path = Path(__file__).parent / 'sample_salla_orders.xlsx'
    df.to_excel(output_path, index=False, engine='openpyxl')
    
    print(f"✅ Sample data generated: {output_path}")
    print(f"   - Total orders: {len(df)}")
    print(f"   - Unique customers: {df['customer_id'].nunique()}")
    print(f"   - Date range: {df['order_date'].min()} to {df['order_date'].max()}")
    print(f"   - Total revenue: SAR {df['order_total'].sum():,.2f}")
    print(f"   - Products: {df['product_name'].nunique()}")
    print(f"   - Categories: {df['category'].nunique()}")
    
    # Show sample
    print("\nSample rows:")
    print(df.head(3))

if __name__ == '__main__':
    main()