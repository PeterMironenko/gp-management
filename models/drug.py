from models import db

class DrugModel(db.Model):
    __tablename__ = 'drugs'

    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(100), unique=False, nullable=False)
    generic_name = db.Column(db.String(100), unique=False, nullable=True)
    form = db.Column(db.String(50), unique=False, nullable=True)
    strength = db.Column(db.String(50), unique=False, nullable=True)
    manufacturer = db.Column(db.String(100), unique=False, nullable=True)
    description = db.Column(db.Text, unique=False, nullable=True)
    is_approval_required = db.Column(db.Boolean, unique=False, nullable=False, default=True)

    def json(self):
        return {
            'id': self.id,
            'drug_name': self.drug_name,
            'generic_name': self.generic_name,
            'form': self.form,
            'strength': self.strength,
            'manufacturer': self.manufacturer,
            'description': self.description,
            'is_approval_required': self.is_approval_required
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def find_by_name(cls, drug_name):
        return cls.query.filter_by(drug_name=drug_name).first() 


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()