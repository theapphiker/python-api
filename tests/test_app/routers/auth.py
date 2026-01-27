from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import database, schemas, utils, oauth2


router = APIRouter(tags=['Authentication'])

# need to use form data for this now
@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    with database.conn.cursor() as cursor:
        cursor.execute("""SELECT * FROM dev.users WHERE email = %s;""", (user_credentials.username,))
        user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    if not utils.verify(user_credentials.password, user.get('password')):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid credentials')
    access_token = oauth2.create_access_token(data = {"user_id": user.get('id')})
    return {"access_token" : access_token, "token_type": "bearer"}