# Inventory Management System

An inventory management system built with Django, Tailwind CSS, PostgreSQL, and HTML. This system helps businesses manage stock efficiently with a structured approval workflow for stock requests and user access control.

## Features

- **Role-Based Access Control**: Users can select their roles during registration, and access is granted after approval by Internal Control.
- **Two-Step Approval Workflow**: Supervisor requests require approval from both the Coordinator and General Manager.
- **Stock Management**: Inventory Managers can add categories, create items, and track stock movements.
- **Procurement Management**: Procurement team members can update stock balances, subject to Inventory Manager approval.
- **User Approval System**: Internal Control approves new user accounts before they can log in.
- **Request Tracking**: Supervisors can request products, and approvals are tracked within the system.

## User Roles & Permissions

| Role                | Permissions |
|---------------------|-------------|
| **Inventory Manager** | Creates items, categories, records stock movements, and approves procurement updates. |
| **Supervisor**       | Requests products. |
| **Procurement**      | Adds new stock balances (requires Inventory Manager approval). |
| **Coordinator**      | First-level approval for Supervisor requests. |
| **General Manager**  | Final approval for Supervisor requests. |
| **Internal Control** | Oversees all activities and approves new user accounts. |

## Installation & Setup

1. Clone the repository:
   ```sh
   git clone <repository_url>
   cd inventory-management
   ```
2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Configure environment variables (e.g., database settings for PostgreSQL).
5. Apply migrations:
   ```sh
   python manage.py migrate
   ```
6. Create a superuser (optional for admin access):
   ```sh
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```sh
   python manage.py runserver
   ```

## Demo Login Credentials

To test the software and approve new user accounts, use the following credentials:

- **Username**: `inventorytestuser`
- **Password**: `K@Tm|,}WEb!<p=?:`

Once logged in, you can approve new users and test different functionalities.

## License

This project is **not open-source** and is intended for private use.

## Contact

For inquiries or contributions, contact me at **winnerbrown9@gmail.com**.
