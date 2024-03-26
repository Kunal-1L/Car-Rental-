# Import necessary modules and classes
from flask import Flask, render_template, request, flash, redirect, session, url_for
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from urllib.parse import quote
import os

# Initialize the Flask app
app = Flask(__name__, static_url_path='/static')

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Configure the upload folder and database URI
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:' + quote('Kunal@123') + '@localhost/CarService'

# Initialize the SQLAlchemy database
db = SQLAlchemy(app)

# Define the Car model
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    car_name = db.Column(db.String(50), nullable=False)
    price_per_day = db.Column(db.String(10), nullable=False)
    image_filepath = db.Column(db.String(255), nullable=False)
    car_details = db.Column(db.TEXT, nullable=False)
    status = db.Column(db.String(10), nullable=False)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15), nullable=False)

# Define the Reservation model
class Reservation(db.Model):
    __tablename__ = 'reservation'  # Add this line to explicitly set the table name
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable = False)
    car_id = db.Column(db.Integer, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    pick_up_date = db.Column(db.String(10), nullable=False)
    pick_up_time = db.Column(db.String(5), nullable=False)
    drop_off_date = db.Column(db.String(10), nullable=False)
    drop_off_time = db.Column(db.String(5), nullable=False)
    bill = db.Column(db.Integer, nullable=False)

# Define the route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Define the route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if the form is submitted using POST
    if request.method == 'POST':
        username = request.form['UserName']
        password = request.form['Password']
        contact = request.form['Contact']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            msg = 'Username already exists. Please choose a different username.'
            
            # Render the registration.html template with an error message
            return render_template('registration.html', msg=msg)

        # Create a new user and add it to the database
        new_user = User(username=username, password=password, contact=contact)
        db.session.add(new_user)
        db.session.commit()

        msg = 'Registration successful! You can now login.'
        
        # Render the login.html template with a success message
        return render_template('login.html', msg=msg)

    # Render the registration.html template for GET requests
    return render_template('registration.html')

# Define the route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the form is submitted using POST
    if request.method == 'POST':
        username = request.form['UserName']
        password = request.form['Password']

        # Check if the user with the given username and password exists
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            # Set the 'logged_in' session variable to True
            session['logged_in'] = True
            session['user_id'] = user.id
            msg = 'Login successful!'
            
            # Redirect to the 'home' route after successful login
            return redirect(url_for('home'))

        else:
            msg = "Login failed. Please check your username and password."
            
            # Render the login.html template with an error message
            return render_template('login.html', msg=msg)

    # Render the registration.html template for GET requests
    return render_template('registration.html')

# Define the route for the home page
@app.route('/home')
def home():
    # Check if the user is logged in
    if 'logged_in' in session and session['logged_in']:
        # Get all cars from the database
        with app.app_context():
            cars = Car.query.all()
            
        # Render the gallery.html template with cars and login status
        return render_template('gallery.html', cars=cars, logged_in=session['logged_in'])
    else:
        # Render the index.html template for non-logged-in users
        return render_template('index.html')
    
# Define the route for the login form
@app.route('/login-form')
def sendLog():
    return render_template('login.html')

# Define the route for the registration form
@app.route('/register-form')
def sendReg():
    return render_template('registration.html')

# Define the route for user logout
@app.route('/logout')
def logout():
    # Log out the user and redirect to the thank-you page
    session['logged_in'] = False
    flash('Logged out successfully.', 'success')
    
    # Redirect to the 'thanks' route
    return redirect(url_for('thanks'))

# Define the route for the car gallery
@app.route('/gallery')
def gallery():
    # Get all cars from the database
    with app.app_context():
        cars = Car.query.all()
    
    # Get the login status from the session
    logged_in = session.get('logged_in', False)
    
    # Render the gallery.html template with the cars and login status
    return render_template('gallery.html', logged_in=logged_in, cars=cars)

# Define the route for the admin page
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if all required fields are present in the form data and if 'image' is in the files
    if all(field in request.form for field in ['firstName', 'lastName', 'email', 'carName', 'pricePerDay', 'carDetails']) and 'image' in request.files:
        # Extract form data
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        car_name = request.form['carName']
        price_per_day = request.form['pricePerDay']
        car_details = request.form['carDetails']

        # Get the uploaded image
        image = request.files['image']

        # Check if the filename is not empty
        if image.filename != '':
            # Securely get the filename
            filename = secure_filename(image.filename)

            # Define the file path where the image will be saved
            filepath = os.path.join('static', 'uploads', filename)

            # Create the 'uploads' folder if it doesn't exist
            if not os.path.exists(os.path.join(app.static_folder, 'uploads')):
                os.makedirs(os.path.join(app.static_folder, 'uploads'))

            # Save the uploaded image to the specified filepath
            image.save(filepath)

            # Save the car information and file path in the SQL database
            with app.app_context():
                new_car = Car(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    car_name=car_name,
                    price_per_day=price_per_day,
                    image_filepath=filename,
                    car_details=car_details,
                    status = False
                )
                db.session.add(new_car)
                db.session.commit()

            # Prepare a success message
            msg = "Your car details uploaded successfully"
            
            # Render the 'thank.html' template with the success message
            return render_template('thank.html', msg=msg)

# Define the route for car booking
@app.route('/booking/<int:car_id>')
def booking(car_id):
    # Retrieve the car information based on car_id
    car = Car.query.get(car_id)
    
    # Get the login status from the session
    logged_in = session.get('logged_in', False)
    
    # Check if the car is found
    if car:
        # Render the Booking.html template with car and login status
        return render_template('Booking.html', car=car, logged_in=logged_in)
    else:
        # Flash a danger message and render the gallery.html template
        flash('Car not found.', 'danger')
        with app.app_context():
            cars = Car.query.all()
        return render_template('gallery.html', cars = cars, logged_in=logged_in)
    
# Define the route for initiating car reservation
@app.route('/bookNow/<int:car_id>')
def book_now(car_id):
    # Check if the user is logged in
    if 'logged_in' in session and session['logged_in']:
        # Retrieve the car information based on car_id
        car = Car.query.get(car_id)

        # Check if the car is found
        if car:
            # Set the car status to True and update the database
            car.status = True
            db.session.commit()

            # Render the reservation.html template with login status and car_id
            return render_template('reservation.html', logged_in=session['logged_in'], car_id=car_id)
        else:
            # Flash a danger message and render the gallery.html template
            flash('Car not found.', 'danger')
            with app.app_context():
                cars = Car.query.all()
            return render_template('gallery.html', cars=cars, logged_in=session.get('logged_in', False))
    else:
        # Flash an info message and render the login.html template
        flash('You need to log in to book a car.', 'info')
        return redirect(url_for('sendLog'))

# Define the route for handling reservation details
@app.route('/reserved', methods=['POST'])
def reserved():
    # Get reservation details from the form
    car_id = request.form.get('car_id')
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    pick_up_date = request.form.get('pickUpDate')
    pick_up_time = request.form.get('pickUpTime')
    drop_off_date = request.form.get('dropOffDate')
    drop_off_time = request.form.get('dropOffTime')

    # Retrieve the car information based on car_id
    car = Car.query.get(car_id)

    if car.status:
        reservations = Reservation.query.filter_by(car_id=car_id).all()
        current_date = datetime.now().date()
        for reservation in reservations:
            drop_off_date_old = datetime.strptime(reservation.drop_off_date, '%Y-%m-%d').date()
            pick_up_date_new = datetime.strptime(pick_up_date, '%Y-%m-%d').date()

            if drop_off_date_old < current_date:
                car.status = False

            if pick_up_date_new < drop_off_date_old:
                msg = "Sorry, but this car is not available."
                with app.app_context():
                    cars = Car.query.all()
                return render_template('gallery.html', msg=msg, cars=cars, logged_in=session.get('logged_in', False))

    car.status = True

    # Convert pick-up and drop-off dates/times to datetime objects
    pick_up_datetime = datetime.strptime(f'{pick_up_date} {pick_up_time}', '%Y-%m-%d %H:%M')
    drop_off_datetime = datetime.strptime(f'{drop_off_date} {drop_off_time}', '%Y-%m-%d %H:%M')

    # Check if the drop-off date is after the pick-up date
    if drop_off_datetime > pick_up_datetime:
        # Calculate the number of days
        delta = drop_off_datetime - pick_up_datetime
        num_of_days = delta.days

        # Calculate the bill based on car price per day and number of days
        bill = int(car.price_per_day) * num_of_days
        user_id = session['user_id']
        # Store reservation details in the database
        with app.app_context():
            new_reservation = Reservation(
                user_id = user_id,
                car_id=car_id,
                first_name=first_name,
                last_name=last_name,
                pick_up_date=pick_up_date,
                pick_up_time=pick_up_time,
                drop_off_date=drop_off_date,
                drop_off_time=drop_off_time,
                bill=bill,
            )
            db.session.add(new_reservation)
            db.session.commit()

        # Render the bill.html template with car, reservation, and login status
        return redirect(url_for('confirmation', car_id=car_id))
    else:
        # Handle the case where drop-off date is not after pick-up date
        error_message = "Invalid drop-off date. Please select a date after the pick-up date."

        # Render the error.html template with an error message
        return render_template('booking.html', error_message=error_message)

# Define the route for the confirmation page
@app.route('/confirmation/<int:car_id>')
def confirmation(car_id):
    # Retrieve reservation details from the database based on car_id
    reservation = Reservation.query.order_by(Reservation.id.desc()).first()
    car = db.session.query(Car).get(car_id)
    # Render the confirmation template with reservation details
    return render_template('confirmation.html', reservation=reservation, car=car, logged_in=session.get('logged_in', False))

# Define the route for the thank-you page
@app.route('/thanks')
def thanks():
    return render_template('thank.html')

# Define the route for the about page
@app.route('/about')
def about():
    return render_template('about.html', logged_in=session.get('logged_in', False))

# Define the route for the contact page
@app.route('/contact')
def contact():
    return render_template('contact.html', logged_in=session.get('logged_in', False))

@app.route('/footer')
def footer():
    return render_template('footer.html')

@app.route('/profile')
def profile():
    user = User.query.filter_by(id = session['user_id']).first()
    return render_template('profile.html', user = user)

# Run the Flask app
if __name__ == '__main__':
    # Create tables before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)