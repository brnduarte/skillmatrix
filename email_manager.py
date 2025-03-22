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
DEFAULT_FROM_EMAIL = "admin@example.com"  # This should match a verified sender in your SendGrid account

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
    if not SENDGRID_API_KEY:
        return False, "SendGrid API key not found in environment variables"
    
    # Construct the invitation URL with relative path
    invite_url = f"/?token={token}"
    
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
    
    message = Mail(
        from_email=DEFAULT_FROM_EMAIL,
        to_emails=email,
        subject='You\'ve Been Invited to Skill Matrix Platform',
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        if response.status_code >= 200 and response.status_code < 300:
            # Update invitation status to "sent"
            update_invitation_status(token, "sent")
            return True, f"Invitation email sent to {email}"
        else:
            return False, f"Failed to send email: {response.status_code} {response.body}"
    except Exception as e:
        return False, f"Error sending email: {str(e)}"

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
    
    return True, invitation.to_dict()

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