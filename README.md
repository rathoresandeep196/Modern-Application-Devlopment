🛒 E-Commerce Web Application using Flask
📌 Description
This project is a full-stack web application developed using Flask as the backend framework and Jinja2 for templating, combined with HTML, CSS, and Font Awesome for the frontend. The application also integrates SQLite as the database, managed efficiently using SQLAlchemy ORM. The project focuses on delivering a user-friendly, secure, and visually appealing e-commerce experience.

It includes user authentication, role-based access control, product management, cart functionality, and order placement. Admin users have extended capabilities to manage product categories and perform CRUD operations, while regular users can browse and purchase products.

🛠 Technologies Used
Python (Flask Framework)

Jinja2 Templating

SQLite Database

SQLAlchemy ORM

HTML5 & CSS3

Font Awesome

Flask Libraries and Extensions

📁 Project Structure
graphql
Copy
Edit
mad1/
│
├── templates/             # All HTML templates
├── static/                # Static files like CSS, JS (currently empty)
├── instance/              # Contains the SQLite database
├── main.py                # Core application with routes and models
├── requirements.txt       # List of dependencies

🔐 Features
User Authentication (Login/Logout)

Role-Based Access:

Users: View products, add to cart, and place orders

Admins: Manage categories and products (CRUD operations)

Product categorization for better organization

Clean and intuitive UI using HTML/CSS and Font Awesome icons
