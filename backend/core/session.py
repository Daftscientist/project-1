import datetime


session_data = {}
users_sessions = {}

def add_user(max_sessions, last_login, latest_ip, signup_ip, session_id, uuid, email, username, avatar, google_account_identifier, discord_account_identifier, created_at):
    if uuid in users_sessions:
        if len(users_sessions[uuid]) >= max_sessions:
            return None
    
    session_data[session_id] = {
        "uuid": uuid,
        "username": username,
        "email": email,
        "avatar": avatar,
        "last_login": last_login,
        "latest_ip": latest_ip,
        "signup_ip": signup_ip,
        "max_sessions": max_sessions,
        "google_account_identifier": google_account_identifier,
        "discord_account_identifier": discord_account_identifier,
        "created_at": created_at, 
        "session_id": session_id
    }

    if not uuid in users_sessions:
        usr_sessions = list()
        usr_sessions.append({session_id: {"timestamp": datetime.datetime.now(), "latest_ip": latest_ip}})
        users_sessions[uuid] = usr_sessions
    else:
        usr_sessions = users_sessions[uuid]
        usr_sessions.append({session_id: {"timestamp": datetime.datetime.now(), "latest_ip": latest_ip}})
        users_sessions[uuid] = usr_sessions

    return session_data[session_id]

def get_user(session_id):
    try:
        return session_data[session_id]
    except KeyError:
        return None

def edit_user(session_id, username: str = None, email: str = None, avatar: str = None, last_login: datetime.datetime = None, latest_ip: str = None, signup_ip: str = None, max_sessions: str = None, google_account_identifier: str = None, discord_account_identifier: str = None) -> dict:
    if email:
        session_data[session_id]["email"] = email
    if username:
        session_data[session_id]["username"] = username
    if avatar:
        session_data[session_id]["avatar"] = avatar
    if last_login:
        session_data[session_id]["last_login"] = last_login
    if latest_ip:
        session_data[session_id]["latest_ip"] = latest_ip
    if signup_ip:
        session_data[session_id]["signup_ip"] = signup_ip
    if max_sessions:
        session_data[session_id]["max_sessions"] = max_sessions
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