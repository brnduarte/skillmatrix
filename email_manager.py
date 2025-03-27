"""
Email functionality for user invitations and notifications using SendGrid
"""
import os
import secrets
import string
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime, timedelta
import pandas as pd

# Load SendGrid API key from environment
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
# Use a default sender email or allow overriding via environment variable
# Ensure we get the environment variable and not hardcoded values
DEFAULT_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL')
if not DEFAULT_FROM_EMAIL or DEFAULT_FROM_EMAIL == "brnduarte@gmail.com":
    # Only use a fallback if no valid environment variable is found
    DEFAULT_FROM_EMAIL = "noreply@skillmatrix.com"
    print(f"WARNING: Using fallback sender email {DEFAULT_FROM_EMAIL} - please set SENDGRID_FROM_EMAIL to a verified sender")

# File to store invitation tokens
INVITATIONS_FILE = "invitations.csv"

def ensure_invitations_file():
    """Ensure the invitations CSV file exists with correct structure"""
    if not os.path.exists(INVITATIONS_FILE):
        df = pd.DataFrame(columns=[
            "token", "username", "email", "organization_id", 
            "created_at", "expires_at", "role", "status"
        ])
        df.to_csv(INVITATIONS_FILE, index=False)
    return pd.read_csv(INVITATIONS_FILE)

def generate_invitation_token():
    """Generate a secure random token for email invitation links"""
    # Create a random string of letters and digits
    alphabet = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(32))
    return token

def create_invitation(username, email, role, organization_id=None, expiry_days=7):
    """
    Create a new invitation record
    
    Args:
        username: Username for the invited user
        email: Email address to send the invitation to
        role: User role (employee, manager, admin)
        organization_id: ID of the organization user will be part of
        expiry_days: Number of days until the invitation expires
        
    Returns:
        Tuple of (success, message, token)
    """
    # Load or create invitations file
    invitations_df = ensure_invitations_file()
    
    # If organization_id is None, empty string or NaN, set to None explicitly
    if organization_id is None or pd.isna(organization_id) or organization_id == '':
        organization_id = None
    
    # Check if invitation already exists for this email
    existing = invitations_df[invitations_df["email"] == email]
    if not existing.empty and any(existing["status"] == "pending"):
        # Update existing pending invitation
        idx = existing[existing["status"] == "pending"].index[0]
        token = generate_invitation_token()
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expires_at = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d %H:%M:%S")
        
        invitations_df.at[idx, "token"] = token
        invitations_df.at[idx, "username"] = username
        invitations_df.at[idx, "role"] = role
        invitations_df.at[idx, "organization_id"] = organization_id
        invitations_df.at[idx, "created_at"] = created_at
        invitations_df.at[idx, "expires_at"] = expires_at
        invitations_df.at[idx, "status"] = "pending"
    else:
        # Create new invitation
        token = generate_invitation_token()
        
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expires_at = (datetime.now() + timedelta(days=expiry_days)).strftime("%Y-%m-%d %H:%M:%S")
        
        new_invitation = pd.DataFrame({
            "token": [token],
            "username": [username],
            "email": [email],
            "organization_id": [organization_id],
            "created_at": [created_at],
            "expires_at": [expires_at],
            "role": [role],
            "status": ["pending"]
        })
        
        invitations_df = pd.concat([invitations_df, new_invitation], ignore_index=True)
    
    # Save invitations file
    invitations_df.to_csv(INVITATIONS_FILE, index=False)
    
    print(f"Created invitation with token: {token}, organization_id: {organization_id}, role: {role}")
    return True, "Invitation created successfully", token

def send_invitation_email(email, token, name=None, organization_name=None):
    """
    Send invitation email to new user
    
    Args:
        email: Recipient email address
        token: Invitation token
        name: Optional name of the recipient
        organization_name: Optional name of the organization
        
    Returns:
        Tuple of (success, message)
    """
    # First check if required secrets exist
    if not SENDGRID_API_KEY:
        return False, "SendGrid API key not found in environment variables. Please set the SENDGRID_API_KEY environment variable."
        
    # Never use the recipient email as the sender
    sender_email = DEFAULT_FROM_EMAIL
    if sender_email == email:
        return False, f"Cannot use recipient email as sender. Please set a different SENDGRID_FROM_EMAIL in environment variables."
    
    # Construct the invitation URL with full path
    # Get the base URL from environment variable or use a default for local testing
    # Use the specific URL for the application
    base_url = 'https://skilltracker.replit.app'
        
    # Create full URL with token parameter
    invite_url = f"{base_url}/?token={token}"
    
    # Personalize the greeting
    greeting = f"Hello {name}," if name else "Hello,"
    
    # Personalize the organization reference
    org_text = f"You've been invited to join {organization_name} on the Skill Matrix platform." if organization_name else "You've been invited to join the Skill Matrix platform."
    
    # Construct the email content
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #3366cc;">Skill Matrix Invitation</h2>
        <p>{greeting}</p>
        <p>{org_text}</p>
        <p>This platform will help track your professional skills and competencies, facilitating your growth and development.</p>
        <p>Click the button below to accept your invitation and set up your account:</p>
        <p style="text-align: center; margin: 30px 0;">
            <a href="{invite_url}" style="background-color: #3366cc; color: white; padding: 12px 20px; text-decoration: none; border-radius: 4px; font-weight: bold;">Accept Invitation</a>
        </p>
        <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
        <p>{invite_url}</p>
        <p>This invitation will expire in 7 days.</p>
        <p>If you have any questions, please contact your administrator.</p>
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
        <p style="color: #999; font-size: 12px;">If you received this email by mistake, please disregard it.</p>
    </div>
    """
    
    try:
        # Log the sender email for debugging
        print(f"Using sender email: {DEFAULT_FROM_EMAIL}")
        
        message = Mail(
            from_email=DEFAULT_FROM_EMAIL,
            to_emails=email,
            subject='You\'ve Been Invited to Skill Matrix Platform',
            html_content=html_content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        if response.status_code >= 200 and response.status_code < 300:
            # Update invitation status to "sent"
            update_invitation_status(token, "sent")
            return True, f"Invitation email sent to {email}"
        else:
            error_body = getattr(response, 'body', 'No detailed error')
            error_msg = (f"SendGrid API error (HTTP {response.status_code}): {error_body}. "
                       f"Please check that your API key has the correct permissions and "
                       f"that '{DEFAULT_FROM_EMAIL}' is a verified sender in your SendGrid account.")
            return False, error_msg
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg:
            error_msg = (f"Error sending email: {error_msg}. This is typically caused by: "
                       f"1) Your SendGrid API key doesn't have permission to send emails, or "
                       f"2) The sender email '{DEFAULT_FROM_EMAIL}' is not verified in your SendGrid account. "
                       f"Please verify your sender email in SendGrid or set SENDGRID_FROM_EMAIL to a verified address.")
        return False, error_msg

def update_invitation_status(token, status):
    """
    Update the status of an invitation
    
    Args:
        token: Invitation token
        status: New status (sent, accepted, expired, etc.)
        
    Returns:
        Boolean indicating success
    """
    if not os.path.exists(INVITATIONS_FILE):
        return False
    
    invitations_df = pd.read_csv(INVITATIONS_FILE)
    
    if invitations_df.empty or "token" not in invitations_df.columns:
        return False
    
    if token not in invitations_df["token"].values:
        return False
    
    idx = invitations_df[invitations_df["token"] == token].index[0]
    invitations_df.at[idx, "status"] = status
    
    invitations_df.to_csv(INVITATIONS_FILE, index=False)
    return True

def verify_invitation(token):
    """
    Verify if an invitation token is valid and not expired
    
    Args:
        token: Invitation token to verify
        
    Returns:
        Tuple of (is_valid, invitation_data) where invitation_data is None if invalid
    """
    if not os.path.exists(INVITATIONS_FILE):
        return False, None
    
    invitations_df = pd.read_csv(INVITATIONS_FILE)
    
    if invitations_df.empty or "token" not in invitations_df.columns:
        return False, None
    
    if token not in invitations_df["token"].values:
        return False, None
    
    invitation = invitations_df[invitations_df["token"] == token].iloc[0]
    
    # Check if already accepted
    if invitation["status"] == "accepted":
        return False, None
    
    # Check if expired
    now = datetime.now()
    expires_at = datetime.strptime(invitation["expires_at"], "%Y-%m-%d %H:%M:%S")
    
    if now > expires_at:
        # Update status to expired
        update_invitation_status(token, "expired")
        return False, None
    
    # Convert to dictionary and handle organization_id specially
    invitation_dict = invitation.to_dict()
    
    # Handle empty or NaN organization_id properly
    if pd.isna(invitation_dict.get('organization_id')) or invitation_dict.get('organization_id') == '':
        invitation_dict['organization_id'] = None
    
    return True, invitation_dict

def mark_invitation_accepted(token):
    """Mark an invitation as accepted"""
    return update_invitation_status(token, "accepted")

def get_pending_invitations(organization_id=None):
    """
    Get all pending invitations
    
    Args:
        organization_id: Optional organization ID to filter by
        
    Returns:
        DataFrame of pending invitations
    """
    if not os.path.exists(INVITATIONS_FILE):
        return pd.DataFrame()
    
    invitations_df = pd.read_csv(INVITATIONS_FILE)
    
    if invitations_df.empty:
        return pd.DataFrame()
    
    # Filter by status first
    pending = invitations_df[invitations_df["status"] == "pending"]
    
    # Then by organization if specified
    if organization_id is not None:
        try:
            organization_id = int(float(organization_id))
            pending = pending[pending["organization_id"] == organization_id]
        except (ValueError, TypeError):
            # Handle case where organization_id is not a valid numeric value
            pass
    
    return pending