from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return{
            "id": self.id,
            "title": self.title,
            "amount": self.amount,
            "category": self.category,
            "date": self.date.isoformat(),
            "description": self.description
        }

with app.app_context():
    db.create_all()

@app.route("/expenses", methods=['GET'])
@app.route("/expenses/<int:expense_id>", methods=['GET'])
def get_expense(expense_id=None):
    if expense_id:
        expense = Expense.query.get(expense_id)
        if expense:
            return jsonify(expense.to_dict())
        else:
            return jsonify({"Error": "Expense does not found"}), 404
    else:
        expenses = Expense.query.all()
        return jsonify([expense.to_dict() for expense in expenses])
    
@app.route("/expenses", methods=['POST'])
def create_expenses():
    data = request.json
    new_expense = Expense(
        title = data['title'],
        amount=data['amount'],
        category=data['category'],
        date=datetime.fromisoformat(data.get('date', datetime.utcnow().isoformat())),
        description=data.get('description', '')
    )
    db.session.add(new_expense)
    db.session.commit()
    return jsonify(new_expense.to_dict()), 201

@app.route("/expense/<int:expense_id>", methods=['PUP'])
def update_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        data = request.json
        expense.title = data['title']
        expense.amount = data['amount']
        expense.category = data['category']
        expense.date = datetime.fromisoformat(data.get('date', expense.date.isoformat()))
        expense.description = data.get('description', '')
        db.session.commit()
        return jsonify(expense.to_dict())
    else:
        return jsonify({"error": "Expense not found"}), 404

@app.route('/expenses/<int:expense_id>', methods=['PATCH'])
def patch_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        data = request.json
        if 'title' in data:
            expense.title = data['title']
        if 'amount' in data:
            expense.amount = data['amount']
        if 'category' in data:
            expense.category = data['category']
        if 'date' in data:
            expense.date = datetime.fromisoformat(data['date'])
        if 'description' in data:
            expense.description = data['description']
        db.session.commit()
        return jsonify(expense.to_dict())
    else:
        return jsonify({"error": "Expense not found"}), 404

@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({"message": "Expense deleted"})
    else:
        return jsonify({"error": "Expense not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)