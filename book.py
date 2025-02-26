from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import os

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# เชื่อมต่อ MongoDB Atlas (ใช้ environment variable หรือซ่อนไม่ให้ใส่ใน GitHub)
MONGO_URI = os.getenv("mongodb+srv://USER:password@cluster0.qp5pw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["bookstore"]  # ตั้งชื่อ database เป็น "bookstore"
collection = db["books"]   # ตั้งชื่อ collection เป็น "books"

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Create (POST) - เพิ่มหนังสือใหม่ลง MongoDB
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data.get("title") or not data.get("author") or not data.get("image_url"):
        return jsonify({"error": "Missing required fields"}), 400
    
    new_book = {
        "title": data["title"],
        "author": data["author"],
        "image_url": data["image_url"]
    }
    
    inserted_book = collection.insert_one(new_book)
    new_book["_id"] = str(inserted_book.inserted_id)  # แปลง ObjectId เป็น string
    return jsonify(new_book), 201

# Read (GET) - ดึงรายการหนังสือทั้งหมดจาก MongoDB
@app.route('/books', methods=['GET'])
def get_all_books():
    books = list(collection.find({}, {"_id": 0}))  # เอา `_id` ออกเพื่อให้ frontend ใช้ง่าย
    return jsonify({"books": books})

# Read (GET) - ดึงหนังสือที่มี ID เฉพาะ
@app.route('/books/<book_title>', methods=['GET'])
def get_book(book_title):
    book = collection.find_one({"title": book_title}, {"_id": 0})
    if book:
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

# Update (PUT) - แก้ไขข้อมูลหนังสือ
@app.route('/books/<book_title>', methods=['PUT'])
def update_book(book_title):
    data = request.get_json()
    update_result = collection.update_one({"title": book_title}, {"$set": data})
    
    if update_result.matched_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book updated successfully"}), 200

# Delete (DELETE) - ลบหนังสือออกจาก MongoDB
@app.route('/books/<book_title>', methods=['DELETE'])
def delete_book(book_title):
    delete_result = collection.delete_one({"title": book_title})
    
    if delete_result.deleted_count == 0:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book deleted successfully"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
