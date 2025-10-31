from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from flask_session import Session
import pymysql
from flask import flash
from flask_cors import CORS
import requests, base64, cv2, json
import numpy as np
import pymysql.cursors
import bcrypt
import re
from functools import wraps
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for mobile app access
CORS(app)

# ---------------------------  
# 🔐 SESSION CONFIG
# ---------------------------
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

# ---------------------------
# 🗄️ DATABASE CONFIG (Railway-compatible with PyMySQL)
# ---------------------------
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DB', 'pinoyluto_db'),
    'cursorclass': pymysql.cursors.DictCursor
}

# ---------------------------
# 🗄️ DATABASE MIGRATION (Run on first deploy)
# ---------------------------
def get_db_connection():
    return pymysql.connect(**db_config)

def init_db():
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            with open('pinoyluto_db_railway.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
            for statement in statements:
                if statement:
                    cursor.execute(statement)

            connection.commit()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database init error: {e}")
    finally:
        connection.close()

# Run migration on app startup (only if tables don't exist)
try:
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            init_db()
    connection.close()
except Exception as e:
    print(f"DB check error: {e}")

# ---------------------------
# 🔒 LOGIN PROTECTION DECORATOR
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "loggedin" not in session:
            return redirect(url_for("landing"))
        response = make_response(f(*args, **kwargs))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return decorated_function

# ---------------------------  
# 🤖 AI SETTINGS
# ---------------------------
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "azvtlf6ccogUJKtpM2m9")
ROBOFLOW_PROJECT = "filfood-aumya"
ROBOFLOW_VERSION = 8

# Gemini API Configuration
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# ---------------------------  
# 🏠 LANDING PAGE
# ---------------------------
@app.route("/")
def landing():
    if "loggedin" in session:
        return redirect(url_for("index"))
    if "admin_loggedin" in session:
        return redirect(url_for("admin_dashboard"))
    return render_template("landing.html")

# ---------------------------  
# 🧭 MAIN DASHBOARD
# ---------------------------
@app.route("/index")
@login_required
def index():
    return render_template("index.html", fullname=session.get("fullname"))

# ---------------------------  
# 👤 USER PROFILE
# ---------------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["id"]
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            fullname = request.form.get("fullname")
            email = request.form.get("email")

            # Handle profile picture upload
            profile_pic = None
            if "profile_pic" in request.files:
                file = request.files["profile_pic"]
                if file and file.filename:
                    filename = f"user_{user_id}_{file.filename}"
                    file_path = f"static/profile_pics/{filename}"
                    file.save(file_path)
                    profile_pic = filename

            # Update user info
            update_query = """
                UPDATE users SET fullname = %s, email = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (fullname, email, user_id))

            if profile_pic:
                cursor.execute("UPDATE users SET profile_pic = %s WHERE id = %s", (profile_pic, user_id))

            mysql.connection.commit()
            session["fullname"] = fullname
            flash("Profile updated successfully!")

        elif action == "change_password":
            old_password = request.form.get("old_password")
            new_password = request.form.get("new_password")

            # Verify old password
            cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not bcrypt.checkpw(old_password.encode("utf-8"), user["password"].encode("utf-8")):
                flash("Old password is incorrect.")
            else:
                hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_pw, user_id))
                mysql.connection.commit()
                flash("Password changed successfully!")

        elif action == "delete_account":
            # Soft delete - mark as inactive
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            mysql.connection.commit()
            session.clear()
            return redirect(url_for("landing"))

    # Fetch user data
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    cursor.close()

    return render_template("profile.html", user=user)

# ---------------------------  
# ✅ SIGNUP
# ---------------------------
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() if request.is_json else request.form
    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")

    if not fullname or not email or not password:
        return jsonify({"error": "Please fill out all fields."}), 400

    cursor = None
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        account = cursor.fetchone()

        if account:
            return jsonify({"error": "Account already exists."}), 400

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        cursor.execute(
            "INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)",
            (fullname, email, hashed_pw),
        )
        mysql.connection.commit()
        return jsonify({"message": "Signup successful! Please log in."}), 200

    except Exception as e:
        logging.error(f"Signup error: {e}")
        return jsonify({"error": "Signup failed. Please try again."}), 500
    finally:
        if cursor:
            cursor.close()

# ---------------------------  
# ✅ LOGIN (User + Admin unified)
# ---------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() if request.is_json else request.form
    email_or_user = data.get("email")  # works for both admin username or user email
    password = data.get("password")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 🔹 1️⃣ Check if logging in as admin
    cursor.execute("SELECT * FROM admin WHERE username = %s", (email_or_user,))
    admin = cursor.fetchone()

    if admin and bcrypt.checkpw(password.encode("utf-8"), admin["password"].encode("utf-8")):
        session.clear()
        session["admin_loggedin"] = True
        session["admin_id"] = admin["id"]
        session["admin_name"] = admin["username"]
        cursor.close()
        return jsonify({"message": "Admin login successful!", "redirect": "/admin_dashboard"}), 200

    # 🔹 2️⃣ Check if logging in as regular user
    cursor.execute("SELECT * FROM users WHERE email = %s", (email_or_user,))
    user = cursor.fetchone()
    cursor.close()

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Invalid email/username or password."}), 400

    session.clear()
    session["loggedin"] = True
    session["id"] = user["id"]
    session["fullname"] = user["fullname"]

    return jsonify({"message": "Login successful!", "redirect": "/index"}), 200

# ---------------------------  
# ✅ LOGOUT
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    resp = redirect(url_for("landing"))
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# ---------------------------  
# 🧠 DETECTION ROUTES
# ---------------------------
@app.route("/detect", methods=["GET", "POST"])
@login_required
def detect():
    if request.method == "GET":
        # Clear session if "new" parameter is present
        if request.args.get("new") == "1":
            session.pop("last_detection", None)
        else:
            # Check if there's a stored detection result
            last_detection = session.get("last_detection")
            if last_detection:
                return render_template("result.html", image=last_detection["image"], foods=last_detection["foods"])

    if request.method == "POST":
        file = request.files["image"]
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
        img_path = f"static/{file.filename}"
        cv2.imwrite(img_path, img)

        # Use Roboflow API for food detection
        try:
            # Roboflow inference
            url = f"https://detect.roboflow.com/{ROBOFLOW_PROJECT}/{ROBOFLOW_VERSION}?api_key={ROBOFLOW_API_KEY}&name=YOUR_IMAGE.jpg"
            with open(img_path, "rb") as img_file:
                response = requests.post(url, files={"file": img_file})
            predictions = response.json().get("predictions", [])

            detected_foods = []
            for pred in predictions:
                food_name = pred.get("class", "").strip()
                if food_name:
                    confidence = pred.get("confidence", 0.0)
                    # Use Gemini API for real estimates
                    calories = ask_gemini_for_calories(food_name)
                    ingredients = ask_gemini_for_ingredients(food_name)
                    detected_foods.append({
                        "name": food_name,
                        "confidence": confidence,
                        "calories": calories,
                        "ingredients": ingredients
                    })

            # Store detection result in session and database
            session["last_detection"] = {
                "image": file.filename,
                "foods": detected_foods
            }

            # Save to database for history
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(
                "INSERT INTO detections (user_id, image_path, detected_foods) VALUES (%s, %s, %s)",
                (session["id"], file.filename, json.dumps(detected_foods))
            )
            mysql.connection.commit()
            cursor.close()

            return render_template("result.html", image=file.filename, foods=detected_foods)
        except Exception as e:
            logging.error(f"Detection error: {e}")
            return render_template("result.html", image=None, foods=[], error=str(e))

    return render_template("detect.html")

@app.route("/detect_camera", methods=["POST"])
@login_required
def detect_camera():
    try:
        data = request.get_json()
        image_b64 = data.get("image").split(",")[1]
        # Decode base64 to image
        image_data = base64.b64decode(image_b64)

        # Use Roboflow API for camera detection
        url = f"https://detect.roboflow.com/{ROBOFLOW_PROJECT}/{ROBOFLOW_VERSION}?api_key={ROBOFLOW_API_KEY}&name=YOUR_IMAGE.jpg"
        response = requests.post(url, files={"file": ("image.jpg", image_data, "image/jpeg")})
        predictions = response.json().get("predictions", [])

        # Format predictions for frontend
        formatted_predictions = [{"class": pred.get("class", "")} for pred in predictions if pred.get("class")]
        return jsonify({"predictions": formatted_predictions})
    except Exception as e:
        logging.error(f"Camera detection error: {e}")
        return jsonify({"error": str(e)}), 500

def ask_gemini_for_calories(food_name: str) -> str:
    try:
        prompt = f"Estimate the approximate calories in a typical serving of {food_name} Filipino food. Provide only the number in kcal, e.g., '250 kcal'. If unsure, say 'Unknown'."
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "Unknown"
    except Exception as e:
        logging.error(f"Gemini calories error: {e}")
        return f"Error estimating calories: {str(e)}"

def ask_gemini_for_ingredients(food_name: str) -> str:
    try:
        prompt = f"List the main ingredients for {food_name}, a Filipino dish. Provide a comma-separated list, e.g., 'rice, chicken, soy sauce'. Keep it concise."
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "Unknown"
    except Exception as e:
        logging.error(f"Gemini ingredients error: {e}")
        return f"Error retrieving ingredients: {str(e)}"


# ---------------------------  
# 💬 CHAT
# ---------------------------
@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        question = request.form.get("question", "")
        detected = request.form.get("detected", "")
        if not question:
            return jsonify({"answer": "Please provide a question."})
        result = ask_gemini_chat(question, detected)
        session["history"].append({"role": "user", "text": question})
        session["history"].append({"role": "ai", "text": result})
        session.modified = True

        # Save to database for history
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "INSERT INTO chat_history (user_id, question, response) VALUES (%s, %s, %s)",
            (session["id"], question, result)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({"answer": result})

    return render_template("chat.html", history=session.get("history", []))

@app.route("/clear_chat")
@login_required
def clear_chat():
    session.pop("history", None)
    return redirect(url_for("chat"))

def ask_gemini_chat(user_text: str, detected: str = "") -> str:
    try:
        context = f"You are a helpful Filipino culinary assistant. Detected foods: {detected}. " if detected else "You are a helpful Filipino culinary assistant. "
        prompt = f"{context}Respond to: {user_text}. Keep responses friendly, informative, and focused on Filipino cuisine."
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "Sorry, I couldn't generate a response."
    except Exception as e:
        logging.error(f"Gemini chat error: {e}")
        return f"Error in chat: {str(e)}"

# ---------------------------  
# 🍳 INGREDIENT SELECTOR
# ---------------------------
@app.route("/select", methods=["GET", "POST"])
@login_required
def select():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM ingredients ORDER BY name ASC")
    ingredients = cursor.fetchall()
    suggestions = []

    if request.method == "POST":
        selected = request.form.getlist("ingredients")
        if not selected:
            return render_template("select.html", ingredients=ingredients, suggestions=[])

        # Stub: Gemini removed, provide basic suggestions based on common Filipino dishes
        suggestions = []
        if "chicken" in selected or "pork" in selected:
            suggestions.append({"dish": "Adobo", "matches": selected, "missing": ["soy sauce", "vinegar"], "optional": ["bay leaf", "garlic"]})
        if "rice" in selected:
            suggestions.append({"dish": "Sinigang", "matches": selected, "missing": ["tamarind", "fish"], "optional": ["kangkong", "eggplant"]})
        if not suggestions:
            suggestions = [{"dish": "No suggestions available", "matches": [], "missing": ["Gemini AI removed"], "optional": []}]

    # Ensure suggestions is always a list
    if not isinstance(suggestions, list):
        suggestions = [suggestions]

    return render_template("select.html", ingredients=ingredients, suggestions=suggestions)

# ---------------------------  
# ➕ ADD TO FAVORITES
# ---------------------------
@app.route("/add_favorite", methods=["POST"])
@login_required
def add_favorite():
    user_id = session["id"]
    food_name = request.form.get("food_name")
    if food_name:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO favorites (user_id, food_name) VALUES (%s, %s)", (user_id, food_name))
        mysql.connection.commit()
        cursor.close()
    return redirect(url_for("profile"))

# ---------------------------  
# ➕ ADD CUSTOM INGREDIENT
# ---------------------------
@app.route("/add_ingredient", methods=["POST"])
@login_required
def add_ingredient():
    name = request.form.get("ingredient_name", "").strip().lower()
    category = request.form.get("ingredient_category", "").strip().lower()
    if not name or not category:
        return redirect(url_for("select"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM ingredients WHERE name = %s", (name,))
    existing = cursor.fetchone()

    if existing:
        flash(f"⚠️ Ingredient '{name}' already exists, skipping insert.")
        return redirect(url_for("select"))

    cursor.execute("INSERT INTO ingredients (name, category) VALUES (%s, %s)", (name, category))
    mysql.connection.commit()
    cursor.close()

    flash(f"✅ Ingredient '{name}' added successfully.")
    return redirect(url_for("select"))

# ---------------------------  
# ✏️ EDIT INGREDIENT
# ---------------------------
@app.route("/edit_ingredient", methods=["POST"])
@login_required
def edit_ingredient():
    ingredient_id = request.form.get("ingredient_id")
    new_name = request.form.get("ingredient_name", "").strip().lower()
    new_category = request.form.get("ingredient_category", "").strip().lower()

    if not ingredient_id or not new_name or not new_category:
        flash("⚠️ Please provide valid ingredient details.")
        return redirect(url_for("select"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("UPDATE ingredients SET name = %s, category = %s WHERE id = %s", (new_name, new_category, ingredient_id))
    mysql.connection.commit()
    cursor.close()

    flash(f"✅ Ingredient '{new_name}' updated successfully.")
    return redirect(url_for("select"))

# ---------------------------  
# 🗑️ DELETE INGREDIENT
# ---------------------------
@app.route("/delete_ingredient/<int:ingredient_id>", methods=["POST"])
@login_required
def delete_ingredient(ingredient_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM ingredients WHERE id = %s", (ingredient_id,))
    mysql.connection.commit()
    cursor.close()

    flash(f"🗑️ Ingredient deleted successfully.")
    return redirect(url_for("select"))

# ---------------------------  
# 🧑‍💼 ADMIN DASHBOARD
# ---------------------------
@app.route("/admin_dashboard")
def admin_dashboard():
    if "admin_loggedin" not in session:
        return redirect(url_for("landing"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT COUNT(*) AS user_count FROM users")
    user_count = cursor.fetchone()["user_count"]

    cursor.execute("SELECT COUNT(*) AS ingredient_count FROM ingredients")
    ingredient_count = cursor.fetchone()["ingredient_count"]
    cursor.close()

    def check_roboflow():
        try:
            test_url = f"https://api.roboflow.com/?api_key={ROBOFLOW_API_KEY}"
            r = requests.get(test_url, timeout=5)
            if r.status_code == 200:
                return {"status": "✅ Online", "version": f"v{ROBOFLOW_VERSION}", "update": "Up to date"}
            else:
                return {"status": "⚠️ Error", "version": "Unknown", "update": "Check API key"}
        except Exception as e:
            return {"status": f"❌ Offline ({str(e)[:25]})", "version": "N/A", "update": "Cannot connect"}

    def check_gemini():
        try:
            # Simple test prompt to check API
            test_response = model.generate_content("Hello")
            if test_response.text:
                return {"status": "✅ Online", "version": "2.0 Flash Exp", "update": "Active"}
            else:
                return {"status": "⚠️ No Response", "version": "2.0 Flash Exp", "update": "Check API key"}
        except Exception as e:
            return {"status": f"❌ Error ({str(e)[:25]})", "version": "2.0 Flash Exp", "update": "Check API key/connection"}

    def check_xampp():
        try:
            r = requests.get("http://localhost", timeout=5)
            if r.status_code == 200:
                return {"status": "✅ Running", "version": "Localhost OK", "update": "Up to date"}
            else:
                return {"status": "⚠️ Error", "version": "Unknown", "update": "Restart Apache/MySQL"}
        except Exception as e:
            return {"status": f"❌ Offline ({str(e)[:25]})", "version": "N/A", "update": "Start XAMPP"}

    return render_template(
        "admin_dashboard.html",
        admin_name=session.get("admin_name"),
        user_count=user_count,
        ingredient_count=ingredient_count,
        roboflow_status=check_roboflow(),
        gemini_status=check_gemini(),
        xampp_status=check_xampp(),
    )

# ---------------------------  
# 👥 ADMIN USER MANAGEMENT API
# ---------------------------
@app.route("/api/users")
def get_users():
    if "admin_loggedin" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, fullname, email FROM users ORDER BY id DESC")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)

@app.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if "admin_loggedin" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({"message": f"User '{user['fullname']}' deleted successfully"})

# ---------------------------  
# 🚀 RUN (Railway-compatible)
# ---------------------------
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
