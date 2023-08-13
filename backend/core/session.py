session_data = {}

def add_user(session_id, uuid, email, username, avatar, google_account_identifier, discord_account_identifier, created_at):
    session_data[session_id] = {
        "uuid": uuid,
        "email": email,
        "username": username,
        "avatar": avatar,
        "google_account_identifier": google_account_identifier,
        "discord_account_identifier": discord_account_identifier,
        "created_at": created_at, 
        "session_id": session_id
    }

def get_user(session_id):
    try:
        return session_data[session_id]
    except KeyError:
        return None

def edit_user(session_id, email: str = None, username: str = None, avatar: str = None, google_account_identifier: str = None, discord_account_identifier: str = None) -> dict:
    if email:
        session_data[session_id]["email"] = email
    if username:
        session_data[session_id]["username"] = username
    if avatar:
        session_data[session_id]["avatar"] = avatar
    if google_account_identifier:
        session_data[session_id]["google_account_identifier"] = google_account_identifier
    if discord_account_identifier:
        session_data[session_id]["discord_account_identifier"] = discord_account_identifier
    return session_data[session_id]

def delete_user(session_id):
    try:
        del session_data[session_id]
    except KeyError:
        return None