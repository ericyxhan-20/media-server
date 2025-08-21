from fastapi import APIRouter, Header, HTTPException
from pathlib import Path
from datetime import datetime
import json
import uuid

router = APIRouter()

@router.post("/auth/signup/")
def auth_signup(username: str, password: str):
    directory = Path('/auth')
    users_path = directory / "users.json"
    tokens_path = directory / "tokens.json"

    try:
        with open(users_path, "r", encoding="utf-8") as file:
            user_data = json.load(file)

        userId = str(uuid.uuid4())
        user_data.append({
            "userId": userId,
            "username": username,
            "password": password,
            "role": "user"
        })

        with open(tokens_path, "r", encoding="utf-8") as file:
            token_data = json.load(file)

        token_data[userId] = []

        with open(users_path, "w", encoding="utf-8") as file:
            json.dump(user_data, file, indent=4, ensure_ascii=False)

        with open(tokens_path, "w", encoding="utf-8") as file:
            json.dump(token_data, file, indent=4, ensure_ascii=False)

        return {"message": "Successfully signed up"}

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Error: Failed to find token file.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Error: Could not decode JSON from token file.")
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Error writing to file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/login/")
def auth_login(username: str, password: str):
    directory = Path('/auth')
    users_path = directory / "users.json"
    tokens_path = directory / "tokens.json"

    try:
        with open(users_path, "r", encoding="utf-8") as file:
            user_data = json.load(file)

        user = next((u for u in user_data if u.get("username") == username and u.get("password") == password), None)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        with open(tokens_path, "r", encoding="utf-8") as file:
            token_data = json.load(file)

        user_tokens = token_data.get(user.get("userId"), [])

        new_token = {
            "tokenId": str(uuid.uuid4()),
            "createdAt": datetime.utcnow().isoformat(),
        }
        user_tokens.append(new_token)
        token_data[user.get("userId")] = user_tokens

        with open(tokens_path, "w", encoding="utf-8") as file:
            json.dump(token_data, file, indent=4, ensure_ascii=False)

        return {"token": new_token, "message": "Successfully logged in"}

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Error: Failed to find token file.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Error: Could not decode JSON from token file.")
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Error writing to file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth/logout/")
def auth_logout(Authorization: str = Header(..., description="Bearer token with 'Bearer ' prefix")):
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token_to_revoke = Authorization.removeprefix("Bearer ").strip()
    tokens_path = Path("/auth/tokens.json")

    try:
        with open(tokens_path, "r", encoding="utf-8") as f:
            tokens_data = json.load(f)

        found = False
        for user, sessions in tokens_data.items():
            for session in sessions:
                if session["tokenId"] == token_to_revoke:
                    sessions.remove(session)
                    found = True
                    break
            if found:
                break

        if not found:
            raise HTTPException(status_code=401, detail="Token not found or already logged out")

        with open(tokens_path, "w", encoding="utf-8") as f:
            json.dump(tokens_data, f, indent=4, ensure_ascii=False)

        return {"message": "Successfully logged out"}

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Error: Failed to find token file.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Error: Could not decode JSON from token file.")
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Error writing to file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/me")
def auth_me(Authorization: str = Header(None)):
    directory = Path('/auth')
    users_path = directory / "users.json"
    tokens_path = directory / "tokens.json"
    
    if Authorization is None or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = Authorization.removeprefix("Bearer ").strip()

    try:
        with open(tokens_path, "r", encoding="utf-8") as file:
            tokens_data = json.load(file)
        
        found = False
        found_userId = None
        for user, sessions in tokens_data.items():
            for session in sessions:
                if session["tokenId"] == token:
                    found = True
                    found_userId = user
                    break
            if found:
                break

        if not found:
            raise HTTPException(status_code=401, detail="Invalid token")
    
        with open(users_path, "r", encoding="utf-8") as file:
            user_data = json.load(file)

        found_user = next((u for u in user_data if u["userId"] == found_userId), None)

        if not found_user:
            raise HTTPException(status_code=401, detail="No valid user found for token")

        return {
            "username": found_user["username"],
            "role": found_user["role"],
        }

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Token database not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Token database is corrupted.")
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Error writing to file: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))