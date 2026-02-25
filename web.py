from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student_result_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    math = db.Column(db.Integer, nullable=False)
    science = db.Column(db.Integer, nullable=False)
    english = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer)
    percentage = db.Column(db.Float)
    grade = db.Column(db.String(2))
    status = db.Column(db.String(10))

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_result', methods=['POST'])
def add_result():
    data = request.get_json()
    
    name = data['name']
    math = int(data['math'])
    science = int(data['science'])
    english = int(data['english'])

    total = math + science + english
    percentage = (total / 300) * 100

    if percentage >= 90:
        grade = "A"
    elif percentage >= 75:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 40:
        grade = "D"
    else:
        grade = "F"

    status = "Pass"
    if math < 40 or science < 40 or english < 40:
        status = "Fail"

    new_result = Result(
        name=name,
        math=math,
        science=science,
        english=english,
        total=total,
        percentage=percentage,
        grade=grade,
        status=status
    )

    db.session.add(new_result)
    db.session.commit()

    return jsonify({
        "message": "Success",
        "name": name,
        "total": total,
        "percentage": percentage,
        "grade": grade,
        "status": status
    })

@app.route('/get_results', methods=['GET'])
def get_results():
    results = Result.query.all()
    result_list = []
    for r in results:
        result_list.append({
            "name": r.name,
            "total": r.total,
            "percentage": r.percentage,
            "grade": r.grade,
            "status": r.status
        })
    return jsonify(result_list)

@app.route('/view_db')
def view_db():
    admin_key = request.args.get('key')
    if admin_key != 'admin123':
        return "Access Denied: You are not authorized to view this page."
        
    results = Result.query.all()
    html = "<h2>Database Records</h2><table border='1' cellpadding='10'><tr><th>ID</th><th>Name</th><th>Math</th><th>Science</th><th>English</th><th>Total</th><th>Percentage</th><th>Grade</th><th>Status</th></tr>"
    for r in results:
        html += f"<tr><td>{r.id}</td><td>{r.name}</td><td>{r.math}</td><td>{r.science}</td><td>{r.english}</td><td>{r.total}</td><td>{r.percentage:.2f}%</td><td>{r.grade}</td><td>{r.status}</td></tr>"
    html += "</table><br><a href='/'>Go Back</a>"
    return html

if __name__ == "__main__":
    app.run(debug=True)
