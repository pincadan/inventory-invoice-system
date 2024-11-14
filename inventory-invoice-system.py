import json
import re
import datetime
import csv
import hashlib
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from fpdf import FPDF
from abc import ABC, abstractmethod

# Authentication and Authorization
class User:
    def __init__(self, username: str, password: str, role: str):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.role = role

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        return self._hash_password(password) == self.password_hash

class Role:
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"

    @staticmethod
    def get_permissions(role: str) -> set:
        permissions = {
            Role.ADMIN: {"all"},
            Role.MANAGER: {"read", "write", "create_invoice", "view_reports"},
            Role.STAFF: {"read", "create_invoice"}
        }
        return permissions.get(role, set())

# Pricing and Discount Rules
class DiscountRule(ABC):
    @abstractmethod
    def apply(self, subtotal: float) -> float:
        pass

class PercentageDiscount(DiscountRule):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def apply(self, subtotal: float) -> float:
        return subtotal * (1 - self.percentage / 100)

class BulkDiscount(DiscountRule):
    def __init__(self, threshold: int, percentage: float):
        self.threshold = threshold
        self.percentage = percentage

    def apply(self, subtotal: float, quantity: int) -> float:
        if quantity >= self.threshold:
            return subtotal * (1 - self.percentage / 100)
        return subtotal

# Export Capabilities
class DataExporter:
    @staticmethod
    def to_csv(data: List[dict], filename: str):
        if not data:
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    @staticmethod
    def to_pdf(title: str, content: str, filename: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=title, ln=1, align='C')
        
        # Add content
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=content)
        pdf.output(filename)

# Enhance existing classes with new features
@dataclass
class Product:
    id: str
    name: str
    price: float
    quantity: int
    category: 'ProductCategory'
    reorder_level: int = 10
    discount_rules: List[DiscountRule] = None

    def __post_init__(self):
        if self.discount_rules is None:
            self.discount_rules = []

    def get_price(self, quantity: int = 1) -> float:
        price = self.price * quantity
        for rule in self.discount_rules:
            if isinstance(rule, BulkDiscount):
                price = rule.apply(price, quantity)
            else:
                price = rule.apply(price)
        return price

class InventorySystem:
    def __init__(self, data_file: str = "inventory_data.json"):
        self.data_file = data_file
        self.products: Dict[str, Product] = {}
        self.customers: Dict[str, Customer] = {}
        self.invoices: Dict[str, Invoice] = {}
        self.users: Dict[str, User] = {}
        self.load_data()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.users.get(username)
        if user and user.verify_password(password):
            return user
        return None

    def check_permission(self, user: User, permission: str) -> bool:
        if "all" in Role.get_permissions(user.role):
            return True
        return permission in Role.get_permissions(user.role)

    def export_inventory_report(self, format: str = 'csv'):
        data = [{
            'id': p.id,
            'name': p.name,
            'quantity': p.quantity,
            'price': p.price,
            'category': p.category.value
        } for p in self.products.values()]
        
        if format == 'csv':
            DataExporter.to_csv(data, 'inventory_report.csv')
        elif format == 'pdf':
            content = self.generate_inventory_report()
            DataExporter.to_pdf('Inventory Report', content, 'inventory_report.pdf')

    def generate_product_performance_report(self) -> str:
        report = "Product Performance Report\n" + "="*30 + "\n\n"
        
        product_sales = {}
        product_revenue = {}
        
        # Calculate sales and revenue by product
        for invoice in self.invoices.values():
            if invoice.status == InvoiceStatus.PAID:
                for item in invoice.items:
                    if item.product_id not in product_sales:
                        product_sales[item.product_id] = 0
                        product_revenue[item.product_id] = 0
                    product_sales[item.product_id] += item.quantity
                    product_revenue[item.product_id] += item.total

        # Generate report
        for product_id in product_sales:
            product = self.products[product_id]
            report += f"\nProduct: {product.name}\n"
            report += f"Total Units Sold: {product_sales[product_id]}\n"
            report += f"Total Revenue: ${product_revenue[product_id]:.2f}\n"
            report += f"Current Stock: {product.quantity}\n"
            if product.quantity <= product.reorder_level:
                report += "WARNING: Stock below reorder level\n"

        return report

    def generate_customer_analysis_report(self) -> str:
        report = "Customer Analysis Report\n" + "="*30 + "\n\n"
        
        customer_purchases = {}
        
        # Calculate purchases by customer
        for invoice in self.invoices.values():
            if invoice.status == InvoiceStatus.PAID:
                if invoice.customer_id not in customer_purchases:
                    customer_purchases[invoice.customer_id] = {
                        'total_spent': 0,
                        'total_invoices': 0,
                        'items_bought': 0
                    }
                
                stats = customer_purchases[invoice.customer_id]
                stats['total_spent'] += invoice.total
                stats['total_invoices'] += 1
                stats['items_bought'] += sum(item.quantity for item in invoice.items)

        # Generate report
        for customer_id, stats in customer_purchases.items():
            customer = self.customers[customer_id]
            report += f"\nCustomer: {customer.name}\n"
            report += f"Total Spent: ${stats['total_spent']:.2f}\n"
            report += f"Number of Invoices: {stats['total_invoices']}\n"
            report += f"Total Items Bought: {stats['items_bought']}\n"
            report += f"Average Order Value: ${stats['total_spent']/stats['total_invoices']:.2f}\n"

        return report

def main():
    system = InventorySystem()
    current_user = None
    
    while True:
        if not current_user:
            print("\nLogin Required")
            username = input("Username: ")
            password = input("Password: ")
            current_user = system.authenticate_user(username, password)
            if not current_user:
                print("Invalid credentials!")
                continue

        print("\nInventory and Invoice Management System")
        print("1. Product Management")
        print("2. Customer Management")
        print("3. Invoice Management")
        print("4. Reports")
        print("5. Export Data")
        print("6. Logout")
        print("7. Exit")
        
        choice = input("Enter your choice (1-7): ")
        
        if choice == "4" and system.check_permission(current_user, "view_reports"):
            print("\nReports")
            print("1. Inventory Report")
            print("2. Sales Report")
            print("3. Product Performance Report")
            print("4. Customer Analysis Report")
            subchoice = input("Enter your choice (1-4): ")
            
            if subchoice == "1":
                print(system.generate_inventory_report())
            elif subchoice == "2":
                start_date = input("Start Date (YYYY-MM-DD): ")
                end_date = input("End Date (YYYY-MM-DD): ")
                print(system.generate_sales_report(start_date, end_date))
            elif subchoice == "3":
                print(system.generate_product_performance_report())
            elif subchoice == "4":
                print(system.generate_customer_analysis_report())

        elif choice == "5" and system.check_permission(current_user, "view_reports"):
            print("\nExport Data")
            print("1. Export Inventory Report (CSV)")
            print("2. Export Inventory Report (PDF)")
            print("3. Export Sales Report (CSV)")
            print("4. Export Sales Report (PDF)")
            subchoice = input("Enter your choice (1-4): ")
            
            if subchoice in ["1", "2"]:
                system.export_inventory_report('csv' if subchoice == "1" else 'pdf')
                print(f"Report exported successfully!")

        elif choice == "6":
            current_user = None
            
        elif choice == "7":
            break

if __name__ == "__main__":
    main()
