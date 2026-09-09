from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection

app = Flask(__name__)

# Secret key for login sessions
app.secret_key = "farmer_empowerment_secret_key"


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# FARMER REGISTRATION
# --------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        location = request.form["location"]
        password = request.form["password"]

        # Encrypt password before storing
        hashed_password = generate_password_hash(password)

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO farmers
                (name, email, phone, password, location)
                VALUES (%s, %s, %s, %s, %s)
            """

            values = (
                name,
                email,
                phone,
                hashed_password,
                location
            )

            cursor.execute(query, values)

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for("login"))

        except Exception as e:

            return f"Registration Error: {e}"

    return render_template("register.html")


# --------------------------------------------------
# FARMER LOGIN
# --------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            connection = get_db_connection()

            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT *
                FROM farmers
                WHERE email = %s
            """

            cursor.execute(query, (email,))

            farmer = cursor.fetchone()

            cursor.close()
            connection.close()

            # Check farmer exists
            if farmer:

                # Check password
                if check_password_hash(
                    farmer["password"],
                    password
                ):

                    # Store farmer details in session
                    session["farmer_id"] = farmer["id"]
                    session["farmer_name"] = farmer["name"]

                    return redirect(url_for("dashboard"))

            return "Invalid email or password"

        except Exception as e:

            return f"Login Error: {e}"

    return render_template("login.html")


# --------------------------------------------------
# FARMER DASHBOARD
# --------------------------------------------------
@app.route("/dashboard")
def dashboard():

    # Check login
    if "farmer_id" not in session:

        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        farmer_name=session["farmer_name"]
    )


# --------------------------------------------------
# CROP INFORMATION
# --------------------------------------------------
@app.route("/crops")
def crops():

    # Check login
    if "farmer_id" not in session:

        return redirect(url_for("login"))

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT *
            FROM crops
            ORDER BY crop_name
        """

        cursor.execute(query)

        crops_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "crops.html",
            crops=crops_data
        )

    except Exception as e:

        return f"Crop Information Error: {e}"


# --------------------------------------------------
# MARKET PRICE INFORMATION
# --------------------------------------------------
@app.route("/market")
def market():

    # Check login
    if "farmer_id" not in session:

        return redirect(url_for("login"))

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT *
            FROM market_prices
            ORDER BY price_date DESC
        """

        cursor.execute(query)

        prices = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "market.html",
            prices=prices
        )

    except Exception as e:

        return f"Market Price Error: {e}"


# --------------------------------------------------
# FARMER PROFILE
# --------------------------------------------------
@app.route("/profile")
def profile():

    # Check login
    if "farmer_id" not in session:

        return redirect(url_for("login"))

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        # Get logged-in farmer using session ID
        query = """
            SELECT id,
                   name,
                   email,
                   phone,
                   location,
                   created_at
            FROM farmers
            WHERE id = %s
        """

        cursor.execute(
            query,
            (session["farmer_id"],)
        )

        farmer = cursor.fetchone()

        cursor.close()
        connection.close()

        # If farmer not found
        if farmer is None:

            session.clear()

            return redirect(url_for("login"))

        return render_template(
            "profile.html",
            farmer=farmer
        )

    except Exception as e:

        return f"Profile Error: {e}"


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
@app.route("/logout")
def logout():

    # Clear login session
    session.clear()

    return redirect(url_for("home"))


# --------------------------------------------------
# RUN FLASK APPLICATION
# --------------------------------------------------
if __name__ == "__main__":

    app.run(debug=True)