from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school_final_v4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class StudentResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(20), default="1234")
    math = db.Column(db.Integer)
    science = db.Column(db.Integer)
    english = db.Column(db.Integer)
    total = db.Column(db.Integer)
    percentage = db.Column(db.Float)
    grade = db.Column(db.String(2))
    status = db.Column(db.String(10))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = data.get('name')
    pwd = data.get('password')

    if user == 'admin' and pwd == 'admin':
        return jsonify({"role": "teacher"})
    
    student = StudentResult.query.filter_by(name=user, password=pwd).first()
    if student:
        return jsonify({
            "role": "student",
            "data": {
                "name": student.name, "math": student.math, "science": student.science,
                "english": student.english, "total": student.total, 
                "percentage": student.percentage, "grade": student.grade, "status": student.status
            }
        })
    return jsonify({"role": "error", "message": "Invalid credentials!"})

@app.route('/add_result', methods=['POST'])
def add_result():
    data = request.get_json()
    m, s, e = int(data['math']), int(data['science']), int(data['english'])
    total = m + s + e
    per = round((total / 300) * 100, 2)
    
    # Logic
    status = "Pass" if (m >= 40 and s >= 40 and e >= 40) else "Fail"
    grade = "A" if per >= 80 else "B" if per >= 60 else "C" if per >= 40 else "F"

    new_entry = StudentResult(
        name=data['name'], math=m, science=s, english=e,
        total=total, percentage=per, grade=grade, status=status
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"success": True})

@app.route('/get_all', methods=['GET'])
def get_all():
    results = StudentResult.query.order_by(StudentResult.percentage.desc()).all()
    return jsonify([{
        "id": r.id, "name": r.name, "total": r.total, "percentage": r.percentage,
        "grade": r.grade, "status": r.status
    } for r in results])

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    db.session.delete(StudentResult.query.get(id))
    db.session.commit()
    return jsonify({"success": True})

@app.route('/view_db')
def view_db():
    if request.args.get('key') == 'admin123':
        results = StudentResult.query.all()
        html = "<h2>Full Database Records</h2><table border='1'><tr><th>ID</th><th>Name</th><th>Password</th><th>Math</th><th>Science</th><th>English</th></tr>"
        for r in results:
            html += f"<tr><td>{r.id}</td><td>{r.name}</td><td>{r.password}</td><td>{r.math}</td><td>{r.science}</td><td>{r.english}</td></tr>"
        return html + "</table><br><a href='/'>Back</a>"
    return "Wrong Key!"

if __name__ == "__main__":
    app.run(debug=True)
