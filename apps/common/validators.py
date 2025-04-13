from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Phone number validator
phone_number_regex = r"^\+?1?\d{9,15}$"

phone_validator = RegexValidator(
    regex=phone_number_regex,
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
)

# Image size validator
def validate_image_size(image):
    max_size = 2 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("Image file too large ( > 2 MB).")