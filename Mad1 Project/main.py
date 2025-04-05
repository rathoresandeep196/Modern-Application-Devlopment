from flask import Flask, render_template, request, redirect, url_for,session,flash
from flask_sqlalchemy import SQLAlchemy 
# from flask_migrate import Migrate
from flask_login import LoginManager
import json
import sqlite3
from sqlalchemy import or_
from datetime import datetime

app = Flask(__name__)

# Configure the database URI
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocerydata.sqlite3'
app.config['SECRET_KEY']="mad1project"

# Initialize SQLAlchemy
db = SQLAlchemy(app)
app.app_context().push()

# Define the User Table
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    f_name = db.Column(db.String(70), nullable=True)
    l_name=db.Column(db.String(70),nullable=True)
    is_admin=db.Column(db.Boolean,nullable=False,default=False)
    
# Define the Category Table
class Category(db.Model):
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(70), nullable=False)
    products = db.relationship('Product', backref='category')

# Define the Product Table
class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=False)
    quantity = db.Column(db.Integer(), nullable=False)
    price = db.Column(db.Float, nullable=False)
    manufacture_date = db.Column(db.Date,nullable=False)

# Define the Cart Table
class Cart(db.Model):
    cart_id = db.Column(db.Integer, primary_key=True)
    id_of_user = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    id_of_product = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Define the Order Table
class Order(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    id_of_user = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    id_of_product = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
class Contact(db.Model):
    contact_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(200), nullable=False)




@app.route('/',methods=['GET','POST'])
def Home():
    if 'user_id' not in session:
        return render_template('not_login.html')
    
    user = User.query.filter_by(user_id=session['user_id']).first()
    if user.is_admin:
        return redirect(url_for('admin_page'))
    
    return render_template('main.html',user=user,categories=Category.query.all())
@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search')
    search_type = request.form.get('search_for')
    
    # Initialize an empty results list
    results = []

    if search_type == 'name':
        # Search for products by name
        results = Product.query.filter(Product.product_name.ilike(f"%{search_term}%")).all()
    elif search_type == 'category':
        # Search for products by category name
        results = Product.query.join(Category).filter(Category.category_name.ilike(f"%{search_term}%")).all()
    elif search_type == 'price':
        try:
            price = float(search_term)
            # Search for products by price
            results = Product.query.filter(Product.price <= price).all()
        except ValueError:
            pass  # Handle invalid price input gracefully

    return render_template('search_results.html', results=results)

    
@app.route('/admin')
def admin_page():
    if 'user_id' not in session:
        return render_template('not_login.html')
    
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    return render_template('admin.html',user=user,categories=Category.query.all())
    
    
@app.route('/profile',methods=['GET','POST'])
def Profile():
    if request.method=='GET':
        if 'user_id' not in session:
           return render_template('not_login.html')
        user = User.query.filter_by(user_id=session['user_id']).first() 
        return render_template('profile.html',user=user)
    elif request.method=='POST':
        if 'user_id' not in session:
           return render_template('not_login.html')
        user = User.query.filter_by(user_id=session['user_id']).first()  
        username=request.form.get('username')
        curr_password=request.form.get('cpassword')
        new_password=request.form.get('password')
        f_name=request.form.get('f_name') 
        l_name=request.form.get('l_name')
        if user.password != curr_password:
            return render_template('miss_match_password.html')
        if User.query.filter_by(username=username).first() and username!=user.username:
            return render_template('updated_username_exists.html')
        user.username=username
        user.password=new_password
        user.f_name=f_name
        user.l_name=l_name
       
        db.session.commit()
        return redirect(url_for('Profile'))




@app.route('/login', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                session['user_id'] = user.user_id
                return redirect(url_for('Home'))
            else:
                return render_template('wrong_password.html')
        else:
            return render_template('login_error.html',user=user)

@app.route('/register', methods=['GET', 'POST'])
def Register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('f_name')
        last_name = request.form.get('l_name')
        if User.query.filter_by(username=username).first():
            return render_template('user_exists.html')
        user = User(username=username, password=password, f_name=first_name, l_name=last_name)
        db.session.add(user)
        db.session.commit()
        return render_template('registration_success.html')
@app.route('/add/category',methods=['GET','POST'])
def add_category():
    if 'user_id' not in session:
           return render_template('not_login.html')
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    if request.method=="GET":
        return render_template('add_category.html')
    elif request.method=="POST":
        category_name=request.form.get('categoryName')
        
        category_exists=Category.query.filter_by(category_name=category_name).first()
        if category_exists:
            return render_template('category_exists.html')
        category=Category(category_name=category_name)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('admin_page'))
        
    return render_template('add_category.html')
@app.route('/category/<int:category_id>/open',methods=['GET','POST'])
def open_category(category_id):
    if 'user_id' not in session:
        return render_template('not_login.html')
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    if request.method=='GET':
        category=Category.query.get(category_id)
        return render_template('show_category_details.html',user=user,category=category)
    
    
@app.route('/category/<int:category_id>/edit',methods=['GET','POST'])
def edit_category(category_id):
    if 'user_id' not in session:
        return render_template('not_login.html')
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    if request.method=='GET':
        category=Category.query.filter_by(category_id=category_id).first()
        return render_template('edit_category.html',category=category)
    elif request.method=='POST':
        category=Category.query.get(category_id)
        category_name=request.form.get('categoryName')
        category.category_name=category_name
        
        db.session.commit()
        return redirect(url_for('admin_page'))
        
@app.route('/category/<int:category_id>/delete',methods=['GET','POST'])
def delete_category(category_id):
    if 'user_id' not in session:
           return render_template('not_login.html')
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    if request.method=='GET':
        category=Category.query.get(category_id)
        if not category:
            return redirect(url_for('/admin_page'))
        return render_template('category_delete.html',user=user,category=category)
    elif request.method=="POST":
        category=Category.query.get(category_id)
        if not category:
            return redirect(url_for('/admin_page'))
        for product in category.products:
            db.session.delete(product)
            db.session.commit()
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('admin_page'))
        
@app.route('/cart')
def cart():
    if 'user_id' not in session:
           return render_template('not_login.html')
    user_id=session['user_id']
    product=Cart.query.filter_by(id_of_user=user_id).all()
    return render_template("cart.html",product=product)
@app.route('/buy_product/<int:id>', methods=['GET', 'POST'])
def buy_product(id):
    if 'user_id' not in session:
        return render_template('not_login.html')
    
    user_id = session['user_id']
    
    # Get the cart item by its cart_id
    cart_item = Cart.query.get(id)
    
    if cart_item:
        id_of_product = cart_item.id_of_product
        quantity = cart_item.quantity
        
        # Retrieve the product to get its price
        product_for_price = Product.query.get(id_of_product)
        
        if product_for_price:
            price = product_for_price.price

            # Calculate the total price for the order
            total_price = price * quantity

            # Get the current date and time
            order_date = datetime.now()

            # Create a new order record
            new_order = Order(
                id_of_user=user_id,
                id_of_product=id_of_product,
                quantity=quantity,
                price=price,  # Use the retrieved price
                order_date=order_date
            )

            # Remove the item from the cart
            db.session.delete(cart_item)
            
            # Add the new order to the database
            db.session.add(new_order)
            
            # Commit the changes
            db.session.commit()

    return redirect(url_for('cart'))
@app.route('/add_to_cart/<int:product_id>', methods=['GET', 'POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        return render_template('not_login.html')

    user_id = session['user_id']
    quantity = int(request.form.get('quantity'))
    
    # Check if the product is already in the user's cart
    existing_cart_item = Cart.query.filter_by(id_of_user=user_id, id_of_product=product_id).first()
    
    if existing_cart_item:
        # Product is already in the cart, update the quantity
        return render_template('already_aded_to_cart.html')
    else:
        # Product is not in the cart, add a new entry
        new_cart_item = Cart(id_of_user=user_id, id_of_product=product_id, quantity=quantity)
        db.session.add(new_cart_item)

    db.session.commit()
    return redirect(url_for('cart'))
    
    return redirect(url_for('Home'))
@app.route('/remove_from_cart/<int:cart_id>')
def remove_from_cart(cart_id):
    if 'user_id' not in session:
        return render_template('not_login.html')
    
    cart_item = Cart.query.get(cart_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()

    return redirect('/cart')

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return render_template('not_login.html')

    user_id = session['user_id']
    
    # Fetch all orders for the logged-in user
    user_orders = Order.query.filter_by(id_of_user=user_id).all()
    
    return render_template('orders.html', user_orders=user_orders)
    
        
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return render_template('not_login.html')
@app.route('/category/<int:category_id>/add-product',methods=['GET','POST'])
def add_product(category_id):
    if 'user_id' not in session:
           return render_template('not_login.html')
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    if request.method=='GET':
        category=Category.query.get(category_id)
        
        return render_template('add_product.html',user=user,category=category,categories=Category.query.all())
    elif request.method == 'POST':
        product_name = request.form.get('product_name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        category_of_pro = request.form.get('category')
        man_date_str = request.form.get('manufacture_date')

        # Convert the 'manufacture_date' string to a Python date object
        man_date = datetime.strptime(man_date_str, '%Y-%m-%d').date()

        # Create a Product object with the correct data types
        product = Product(
            product_name=product_name,
            quantity=quantity,
            price=price,
            category_id=category_of_pro,
            manufacture_date=man_date
        )

        # Insert the data into the database
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('open_category', category_id=category_id))
        
@app.route('/product/<int:product_id>/edit',methods=['GET','POST'])
def product_edit(product_id):
    if 'user_id' not in session:
           return render_template('not_login.html')
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    if request.method=='GET':
        product=Product.query.get(product_id)
        return render_template('edit_product.html' ,user=user, product=product,
                               categories=Category.query.all(),
                               manufaticture_date=product.manufacture_date.strftime("%Y-%m-%d"))
    elif request.method=='POST':
        product_name = request.form.get('product_name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        category_of_pro = request.form.get('category')
        man_date_str = request.form.get('manufacture_date')
        # Convert the 'manufacture_date' string to a Python date object
        man_date = datetime.strptime(man_date_str, '%Y-%m-%d').date()
        product=Product.query.get(product_id)
        product.product_name=product_name
        product.quantity=quantity
        product.price=price
        product.category_id=category_of_pro
        product.manufacture_date=man_date
        db.session.commit()
        return redirect(url_for('open_category' ,category_id=product.category_id))
        
        
@app.route('/product/<int:product_id>/delete',methods=['GET','POST'])
def product_delete(product_id):
    if 'user_id' not in session:
           return render_template('not_login.html')
    user = User.query.filter_by(user_id=session['user_id']).first()
    if not user.is_admin:
        return render_template('not_admin.html')
    if request.method=='GET':
        product=Product.query.get(product_id)
        if not product:
            return redirect(url_for('/admin_page'))
        return render_template('delete_product.html' ,user=user,product=product)
    elif request.method=='POST':
        product=Product.query.get(product_id)
        if not product:
            return redirect(url_for('admin_page'))
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('open_category', category_id=product.category_id))
    

@app.route('/submitcontact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')

            if not name or not email or not message:
                flash('Please fill all the required fields.', 'warning')
                return redirect(url_for('contact_form'))

            # Create and save contact entry
            contact = Contact(name=name, email=email, message=message)
            db.session.add(contact)
            db.session.commit()

            flash('Your message has been submitted successfully!', 'success')
            return redirect(url_for('contact_form'))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again later.', 'danger')
            print("Error:", e)
            return redirect(url_for('contact_form'))

# Example route to show contact form page
@app.route('/contact')
def contact_form():
    return render_template('contact.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
        admin=User.query.filter_by(username='admin').first()
        if not admin:
            admin=User(username='admin',password='admin',f_name='admin',l_name='admin',is_admin=True)
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
     