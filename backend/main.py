from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from clickhouse_driver import Client

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(token=Depends(security)):
    try:
        payload = jwt.get_unverified_claims(token.credentials)
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/reports")
def get_report(user=Depends(get_current_user)):
    user_id = user.get("preferred_username") or user.get("sub")

    client = Client(
        host="clickhouse",
        port=9000,
        user="default",
        password="password"
    )

    result = client.execute(
        "SELECT * FROM user_reports WHERE user_id = %(user_id)s",
        {"user_id": user_id}
    )

    if not result:
        return {"message": "Report not ready yet"}

    return {"data": result}