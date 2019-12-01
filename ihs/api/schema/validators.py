from marshmallow import ValidationError

# Custom validator
def not_blank(data):
    if not data:
        raise ValidationError("Data not provided.")

