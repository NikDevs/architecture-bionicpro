from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
from clickhouse_driver import Client

app = FastAPI()
security = HTTPBearer()

KEYCLOAK_PUBLIC_KEY = "YOUR_PUBLIC_KEY"
ALGORITHM = "RS256"

def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(
            token.credentials,
            KEYCLOAK_PUBLIC_KEY,
            algorithms=[ALGORITHM],
            audience="reports-frontend"
        )
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/reports")
def get_report(user=Depends(get_current_user)):
    user_id = user.get("sub")

    client = Client(host='clickhouse')

    result = client.execute(
        "SELECT * FROM user_reports WHERE user_id = %(user_id)s",
        {"user_id": user_id}
    )

    if not result:
        return {"message": "Report not ready yet"}

    return {"data": result}