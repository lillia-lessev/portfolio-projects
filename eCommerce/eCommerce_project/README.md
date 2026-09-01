# eCommerce Application

A Django eCommerce application allowing buyers to view, buy and review products as well as vendors to create stores and sell products.

- Vendors can create stores, manage products (with images, stock, and pricing), and view their inventory.
- Buyers can browse products, add items to a cart, checkout, and leave reviews.
- Includes full authentication (register, login, logout) and password recovery via email.

## Table of Contents

- [Features](#features)
- [Usage](#usage)

## Features

- User registration with account type (Vendor / Buyer)
- Login / Logout
- Password reset via email (Gmail SMTP)
- Vendor store management (create, edit, delete)
- Product management (create, edit, delete, upload images)
- Product listing and detail pages
- Shopping cart (session-based)
- Checkout and order creation
- Product reviews and ratings
- Users can browse Vendors / Stores / Products
- MySQL database

### Tech Stack

- **Python**
- **Django**
- **`python-dotenv`**
- **`Pillow` (for product image uploads)**

## Usage

1. Clone the repository

    ```bash
    git clone https://github.com/lillia-lessev/portfolio-projects.git
    
    cd portfolio-projects/eCommerce/eCommerce_project
    ```

2. Create and activate a virtual environment. 
    Copy and paste the following code into your terminal:

        python -m venv .venv

        # Windows
        .venv\Scripts\activate

        # macOS / Linux
        source venv/bin/activate

3. Install dependencies
    Copy and paste the following code into your terminal:

        pip install -r requirements.txt

4. Configure environment variables (Email / Password Recovery)

    For development purposes, emails (such as password recovery emails and invoice emails) will be printed in the terminal.

    If you want to go live with the application and set-up the emails:

        The application uses Gmail SMTP to send password-reset emails as well as emails for product orders.
        
        To run the application, you will need to configure a real Gmail account and an app password.

        The project folder contains a .env.example file.

        4.1. Copy the example file.

            # Windows
            copy .env.example .env

            # macOS / Linux
            cp .env.example .env

        4.2. Open the .env file and replace the details with your own details.

            # Email (Gmail App Password)
            EMAIL_HOST_USER=yourrealemail@gmail.com
            EMAIL_HOST_PASSWORD=your-16-char-app-password

            # MySQL 
            DB_NAME=ecommerce_db
            DB_USER=django_user1
            DB_PASSWORD=YourStrongPassword123!
            DB_HOST=127.0.0.1
            DB_PORT=3306

        Please note that the database details you fill in need to match the details that you use in the next step.




    If you want to change from emails being printed in the terminal to the SMTP emails, you will need to do the following:

        In the settings.py file located:
            \eCommerce_app\eCommerce_project\eCommerce_project\settings.py
        
        Comment out the following lines of code:

            EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
            DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')
        
        You can comment them out by adding a hashtag symbol ('#') in front of each line.
        You can type them out manually, or, a quick way that you can also do this is to select the  lines you want to comment out and press:

            # Windows
            CTRL + /

            # macOs
            cmd + /

        The lines should look like this in the end:

            # EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
            # DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

        Next, you will need to add the following lines of code:
        (Note these lines of code are already in settings.py, but they are commented out.
        You will need to uncomment them by remowing the hashtag symbols ('#') in front of each line.
        You can do this manually by deleting each hashtag symbol ('#') or selecting the lines and using the commands mentioned in the previous step.)
        You should end up having these lines of code:

            EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
            EMAIL_HOST = 'smtp.gmail.com'
            EMAIL_PORT = 587
            EMAIL_USE_TLS = True
            EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
            EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
            DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')





5. Set up the database in MySQL

        Remember that the details you use in this step need to match the database details you used in the .env file.

    5.1. Open MySQL Workbench and connect as 'root'.
    5.2. Run the following SQL:

        CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

        CREATE USER 'django_user1'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'YourStrongPassword123!';

        GRANT ALL PRIVILEGES ON ecommerce_db.* TO 'django_user1'@'localhost';

        FLUSH PRIVILEGES;

6. Run database migrations

    In the terminal, in the project folder
        \eCommerce_app\eCommerce_project
    run the following code in your terminal:

        python manage.py makemigrations

        python manage.py migrate

7. (Optional) Create a superuser in order to access the admin panel

    In your terminal, run the following code:

        python manage.py createsuperuser

    You will be instructed to choose a username and password.

8. Start the development server

    Run the following code in your terminal:

        python manage.py runserver

    Open the following link in your browser:
        http://127.0.0.1:8000/

    To access the admin panel, use the following link:
        http://127.0.0.1:8000/admin


6. Run database migrations in the terminal

        python manage.py makemigrations
        python manage.py migrate



7. (Optional) Create a superuser for the admin panel

    python manage.py createsuperuser

8. Start the server to run the application with the following command:

    python manage.py runserver


---

Made by [lillia-lessev](https://github.com/lillia-lessev)