# News Application

A Django News application allowing users to browse articles and subscribe to newsletters from journalists and publishers, approved by editors.

- Readers can create an account, login, browse articles approved by editors, see all the relevant journalists and publishers - both independent journalists and those part of a publishing houses - as well as subscribe to individual journalists & / or publishers to receive newsletters (via email and the app) created by journalists. 

- Journalists can either be independent or part of a publisher. Journalists can create, edit, and delete both articles and newsletters (a curated collection of articles).

- Editors can approve articles written by journalists and make them available to be read as well as view, edit and delete articles and newsletters.

- Includes full authentication (register, login, logout) and password recovery via email.

## Table of Contents

- [Features](#features)
-[Tech Stack](#tech-stack)
- [Usage](#usage)


## Features

- User registration with account type (Reader / Journalist / Publisher / Editor)
- Login / Logout
- Users can browse approved articles and publishers & journalists
- Readers can subscribe to journalists &/or publishers to get newsletters created by them
- Journalists and view, create, edit, delete articles + newsletters
- Journalists can be independent or part of a publisher
- Editors can view, edit, delete articles and newsletters
- Editors can approve articles and make them visible to be read by readers
- MariaDB database

### Tech Stack

- **Python**
- **Django**
- **`python-dotenv`**
- **`Pillow` **

## Usage

1. Clone the repository

    ```bash
    git clone https://github.com/lillia-lessev/news_project 
    
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

    For development purposes, emails (such as password recovery emails and newsletter emails) will be printed in the terminal.

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

            # MariaDB
            DB_NAME=news_db
            DB_USER=news_user
            DB_PASSWORD=YourStrongPassword123!
            DB_HOST=127.0.0.1
            DB_PORT=3306

        Please note that the database details you fill in need to match the details that you use in the next step (step #5).




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





5. Set up the database in MariaDB

        Remember that the details you use in this step need to match the database details you used in the .env file.

    5.1. Open MySQL Client (MariaDB)

    5.2. Enter your MariaDB password

    5.3. Run the following SQL:

        CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';

        GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';

        FLUSH PRIVILEGES;

        EXIT;

6. Run database migrations

    In the terminal, in the project folder
        \news_project\
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




---

Made by [lillia-lessev](https://github.com/lillia-lessev)