from fastapi import Response, status, HTTPException, APIRouter, Depends
from app import schemas, database, oauth2
from psycopg import errors

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("/", status_code=status.HTTP_204_NO_CONTENT)
def vote(vote: schemas.Vote, current_user:int = Depends(oauth2.get_current_user)):
    if vote.dir == 1:
        with database.conn.cursor() as cursor:
            try:
            # won't do anything if user already voted for a post
                cursor.execute("""INSERT INTO dev.votes (post_id, user_id) VALUES (%s, %s)
                            ON CONFLICT DO NOTHING;""", 
                            (vote.post_id, current_user.get('id')))
                database.conn.commit()
            except errors.ForeignKeyViolation:
                database.conn.rollback()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {vote.post_id} does not exist")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        with database.conn.cursor() as cursor:
            try:
                # won't do anything if user has not voted for a post
                cursor.execute("""DELETE FROM dev.votes WHERE post_id = %s AND user_id = %s RETURNING *;""", 
                            (vote.post_id, current_user.get('id')))
                database.conn.commit()
            except errors.ForeignKeyViolation:
                database.conn.rollback()
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {vote.post_id} does not exist")
        return Response(status_code=status.HTTP_204_NO_CONTENT)