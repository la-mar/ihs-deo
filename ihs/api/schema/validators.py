from marshmallow import ValidationError

# Custom validator
def not_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


def length_is_14(data):
    target = 14
    if len(data) != target:
        raise ValidationError(f"Incorrect length: {len(data)} (should be {target})")


def length_is_10(data):
    target = 10
    if len(data) != target:
        raise ValidationError(f"Incorrect length: {len(data)} (should be {target})")
