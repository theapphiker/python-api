from datetime import timezone, datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError
import schemas, database
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

load_dotenv()

secret_key = os.getenv('SECRET_KEY')
algorithm = os.getenv('ALGORITHM')
access_token_expire_minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        id: str = str(payload.get('user_id'))
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except InvalidTokenError:
        raise credentials_exception
    return token_data

# pass as dependency into any path operation
def get_current_user(token: str = Depends(oauth2_scheme), ):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate credentials',
                                          headers={'WWW-Authenticate':'Bearer'})
    token = verify_access_token(token, credentials_exception)
    with database.conn.cursor() as cursor:
        cursor.execute("""SELECT id, email, created_at FROM dev.users WHERE id = %s;""", (token.id,))
        user = cursor.fetchone()
    return user