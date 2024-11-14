I've created a comprehensive inventory and invoice management system with the following key features:

1. Product Management:
    * Add/update products with validation
    * Track inventory levels
    * Reorder level warnings
    * Product categorization
2. Customer Management:
    * Store customer details
    * Email and phone validation
    * Address tracking
3. Invoice Management:
    * Create and modify invoices
    * Add products to invoices
    * Track invoice status
    * Automatic inventory updates
    * Tax calculations
4. Data Persistence:
    * JSON file storage
    * Automatic saving of changes
5. Reporting:
    * Inventory reports by category
    * Sales reports by date range
    * Low stock warnings
6. Input Validation:
    * Email format checking
    * Phone number format checking
    * Price and quantity validation
The system uses classes and dataclasses for clean organization:
* Product: Manages product information
* Customer: Handles customer data
* Invoice and InvoiceItem: Handle sales transactions
* InventorySystem: Main system class that coordinates everything


I've enhanced the system with several new features:

User Authentication & Authorization:
    * User roles (Admin, Manager, Staff)
    * Permission-based access control
    * Secure password hashing
    * Login/logout functionality
    
Advanced Pricing Rules:
    * Abstract discount rule system
    * Percentage-based discounts
    * Bulk purchase discounts
    * Flexible rule combinations
    
Enhanced Reporting:
    * Product performance analysis
    * Customer purchase analysis
    * Stock level warnings
    * Revenue tracking
    
Data Export Capabilities:
    * CSV export for tabular data
    * PDF report generation
    * Multiple report formats
    * Professional formatting
    
New Reports:
* Product Performance Report
    * Units sold per product
    * Revenue per product
    * Stock warnings
      
* Customer Analysis Report
    * Total spend per customer
    * Average order value
    * Purchase frequency
 
Security Improvements:
* Password hashing
* Role-based access control
* Permission checking
* Secure session management

To use these new features:

For authentication:
user = system.authenticate_user("username", "password")

For discounts:
product.discount_rules.append(PercentageDiscount(10))  # 10% off
product.discount_rules.append(BulkDiscount(10, 15))    # 15% off for 10+ items

For exports:
system.export_inventory_report('csv')  # or 'pdf'

