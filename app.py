"""
Flask Web Application for Chatbot with JWT Auth, SQLite Storage, Admin API, and Ollama RAG Agent.
"""

import os
import sys
import uuid
import threading
import werkzeug.utils
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, create_user, get_user_by_username, get_user_by_id, get_all_users
from auth import generate_token, jwt_required, admin_required
from backend.agent_engine import agent_engine_instance
from backend.llm_engine import llm_engine_instance
from backend.rag_engine import rag_engine_instance
from backend.memory_engine import memory_engine_instance
from config import DEFAULT_MODEL, AVAILABLE_MODELS

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ollama-chatbot-flask-secret-key-2026")
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize DB and Seed Admin directly
init_db()

# Pre-warm RAG embedding model in background so user uploads are fast
threading.Thread(target=rag_engine_instance.warmup_embeddings, daemon=True).start()

current_model = DEFAULT_MODEL



# ==========================================
# PAGE ROUTE
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")


# ==========================================
# AUTHENTICATION ENDPOINTS
# ==========================================

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()

    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Username, email, and password are required"}), 400

    if len(username) < 3:
        return jsonify({"status": "error", "message": "Username must be at least 3 characters long"}), 400

    if len(password) < 4:
        return jsonify({"status": "error", "message": "Password must be at least 4 characters long"}), 400

    existing_user = get_user_by_username(username)
    if existing_user:
        return jsonify({"status": "error", "message": "Username already exists"}), 400

    hashed_pw = generate_password_hash(password)
    try:
        user_id = create_user(username, email, hashed_pw, role="user")
        token = generate_token(user_id, username, "user")
        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "token": token,
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "role": "user"
            }
        }), 201
    except Exception as e:
        return jsonify({"status": "error", "message": f"Could not create account: {str(e)}"}), 500


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"status": "error", "message": "Username and password required"}), 400

    user = get_user_by_username(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"status": "error", "message": "Invalid username or password"}), 401

    token = generate_token(user["id"], user["username"], user["role"])
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    })


@app.route("/api/me", methods=["GET"])
@jwt_required
def get_me():
    user = get_user_by_id(request.current_user["user_id"])
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 444
    return jsonify({"status": "success", "user": user})


# ==========================================
# ADMIN API (User details view for Admin)
# ==========================================

@app.route("/api/admin/users", methods=["GET"])
@admin_required
def admin_get_users():
    """
    API endpoint for admin to see all registered user details.
    Requires Admin JWT token.
    """
    users = get_all_users()
    return jsonify({
        "status": "success",
        "total_users": len(users),
        "users": users
    })


# ==========================================
# CHATBOT & OLLAMA ENDPOINTS
# ==========================================

@app.route("/api/ollama-status", methods=["GET"])
def get_ollama_status():
    global current_model
    is_online, msg, available_models = llm_engine_instance.check_connection()
    pdf_info = None
    if rag_engine_instance.vectorstore is not None:
        pdf_info = {
            "doc_name": rag_engine_instance.doc_name,
            "total_pages": rag_engine_instance.total_pages,
            "total_chunks": rag_engine_instance.total_chunks
        }
    return jsonify({
        "is_online": is_online,
        "message": msg,
        "current_model": current_model,
        "available_models": available_models,
        "pdf_info": pdf_info
    })


@app.route("/api/chat", methods=["POST"])
@jwt_required
def chat():
    global current_model
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    selected_model = data.get("model", current_model)

    if not user_message:
        return jsonify({"status": "error", "message": "Message cannot be empty"}), 400

    tool_used_holder = [None]

    def on_tool(t_name):
        tool_used_holder[0] = t_name

    try:
        res = agent_engine_instance.process_query(
            user_input=user_message,
            model_name=selected_model,
            on_tool_called=on_tool
        )
        return jsonify({
            "status": "success",
            "response": res.get("response"),
            "tool_used": res.get("tool_used") or tool_used_holder[0]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/upload-pdf", methods=["POST"])
@jwt_required
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"status": "error", "message": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "No file selected"}), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"status": "error", "message": "Only PDF files are supported"}), 400

    orig_name = os.path.basename(file.filename)
    safe_name = werkzeug.utils.secure_filename(orig_name)
    if not safe_name or not safe_name.lower().endswith(".pdf"):
        safe_name = f"doc_{uuid.uuid4().hex[:8]}.pdf"

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    try:
        file.save(save_path)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save file: {str(e)}"}), 500

    try:
        result = rag_engine_instance.process_pdf(save_path)
        return jsonify({
            "status": "success",
            "message": "PDF uploaded and indexed successfully",
            "pdf_info": result
        })
    except ValueError as ve:
        return jsonify({"status": "error", "message": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to process PDF: {str(e)}"}), 500



@app.route("/api/clear-pdf", methods=["POST"])
@jwt_required
def clear_pdf():
    rag_engine_instance.reset()
    return jsonify({"status": "success", "message": "PDF detached and index cleared"})


@app.route("/api/clear-memory", methods=["POST"])
@jwt_required
def clear_memory():
    memory_engine_instance.clear()
    return jsonify({"status": "success", "message": "Conversation memory cleared"})


if __name__ == "__main__":
    print("[INFO] Starting Flask Ollama Chatbot App on http://127.0.0.1:5000")
    print("[INFO] Default Admin Credentials: Username: admin | Password: adminpassword")
    app.run(host="0.0.0.0", port=5000, debug=True)
