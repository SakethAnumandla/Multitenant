import re
from email_validator import validate_email, EmailNotValidError

def validate_email_format(email):
    """
    Validate email format
    
    Args:
        email: Email string to validate
    
    Returns:
        Tuple (is_valid: bool, message: str)
    """
    try:
        # Validate and normalize email
        valid = validate_email(email)
        return True, valid.email
    except EmailNotValidError as e:
        return False, str(e)

def validate_password_strength(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    
    Args:
        password: Password string to validate
    
    Returns:
        Tuple (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def validate_phone_number(phone):
    """
    Validate phone number format (Indian format)
    
    Args:
        phone: Phone number string
    
    Returns:
        Tuple (is_valid: bool, message: str)
    """
    if not phone:
        return True, "Phone number is optional"
    
    # Remove spaces and dashes
    phone_cleaned = re.sub(r'[\s\-]', '', phone)
    
    # Indian phone number: 10 digits, optionally starting with +91
    if re.match(r'^(\+91)?[6-9]\d{9}$', phone_cleaned):
        return True, phone_cleaned
    
    return False, "Invalid phone number format. Use 10-digit Indian phone number"

def validate_slug(slug):
    """
    Validate slug format (SEO-friendly URL)
    Should be lowercase, alphanumeric, with hyphens
    
    Args:
        slug: Slug string to validate
    
    Returns:
        Tuple (is_valid: bool, message: str)
    """
    if not slug:
        return False, "Slug cannot be empty"
    
    if len(slug) < 3:
        return False, "Slug must be at least 3 characters long"
    
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        return False, "Slug must be lowercase alphanumeric with hyphens only"
    
    return True, slug

def generate_slug_from_name(name):
    """
    Generate SEO-friendly slug from name
    
    Args:
        name: Business/organization name
    
    Returns:
        Generated slug string
    """
    # Convert to lowercase
    slug = name.lower()
    
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Remove consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    return slug

def validate_gst_number(gst):
    """
    Validate Indian GST number format
    Format: 2 digits (state code) + 10 alphanumeric (PAN) + 1 digit + 1 alphabet + 1 alphanumeric
    
    Args:
        gst: GST number string
    
    Returns:
        Tuple (is_valid: bool, message: str)
    """
    if not gst:
        return True, "GST is optional"
    
    gst = gst.upper().strip()
    
    if re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$', gst):
        return True, gst
    
    return False, "Invalid GST number format"

def validate_pan_number(pan):
    """
    Validate Indian PAN number format
    Format: 5 letters + 4 digits + 1 letter
    
    Args:
        pan: PAN number string
    
    Returns:
        Tuple (is_valid: bool, message: str)
    """
    if not pan:
        return True, "PAN is optional"
    
    pan = pan.upper().strip()
    
    if re.match(r'^[A-Z]{5}\d{4}[A-Z]{1}$', pan):
        return True, pan
    
    return False, "Invalid PAN number format"

