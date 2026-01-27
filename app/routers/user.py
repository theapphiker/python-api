from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from psycopg.rows import dict_row
from app import schemas, utils, database

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db = Depends(database.get_db)):
    cursor, conn = db
    hashed_password = utils.get_password_hash(user.password)
    user.password = hashed_password
    cursor.execute("""INSERT INTO dev.users (email, password) VALUES (%s, %s) RETURNING *""", 
                (user.email, user.password))
    new_user = cursor.fetchone()
    conn.commit()
    return new_user

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db = Depends(database.get_db)):
    cursor, conn = db
    cursor.execute("""SELECT id, email FROM dev.users WHERE id = %s;""", (id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} does not exist")
    return user