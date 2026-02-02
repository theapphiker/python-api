from fastapi import Response, status, HTTPException, APIRouter, Depends
from typing import List, Optional
from app import schemas, database, oauth2

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", response_model=List[schemas.Post])
def get_posts(current_user:int = Depends(oauth2.get_current_user), db = Depends(database.get_db),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    cursor, conn = db
    cursor.execute("""WITH votes AS (SELECT post_id, COUNT(*) AS number_votes
                       FROM dev.votes GROUP BY post_id)
                       
                       SELECT p.id AS post_id, p.title, p.content, p.published,
                       p.created_at AS post_created, COALESCE(number_votes, 0) AS number_votes, json_build_object('id',p.user_id, 'email', u.email, 
                       'created_at',u.created_at) AS user
                        FROM dev.posts p JOIN dev.users u on p.user_id = u.id
                       LEFT JOIN votes v on p.id = v.post_id
                       WHERE p.title ILIKE %s
                       LIMIT %s OFFSET %s;""", (f'%{search}%', limit, skip))
    posts = cursor.fetchall()
    return posts

# send a 201 when creating something
# user has to be authenticated before posting
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, current_user:int = Depends(oauth2.get_current_user), db = Depends(database.get_db)):
    cursor, conn = db
    cursor.execute("""WITH insert_data AS (INSERT INTO dev.posts (title, content, published, user_id) VALUES (%s, %s, %s, %s)
                    RETURNING title, content, published, created_at AS post_created, id AS post_id, user_id)
                    
                    SELECT json_build_object('id', u.id, 'email', u.email, 
                    'created_at',u.created_at) AS user,
                    title, content, published, post_created, post_id, 0 AS number_votes
                    FROM dev.users u
                    JOIN insert_data id
                    ON u.id = id.user_id;""", 
                (post.title, post.content, post.published, current_user.get('id')))
    new_post = cursor.fetchone()
    conn.commit()
    return new_post

@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, current_user:int = Depends(oauth2.get_current_user), db = Depends(database.get_db)):
    cursor, conn = db
    cursor.execute("""WITH votes AS (SELECT post_id, COUNT(*) AS number_votes
                    FROM dev.votes GROUP BY post_id)
                    
                    SELECT p.id AS post_id, p.title, p.content, p.published,
                    p.created_at AS post_created, COALESCE(number_votes, 0) AS number_votes, json_build_object('id',p.user_id, 'email', u.email, 
                    'created_at',u.created_at) AS user
                    FROM dev.posts p JOIN dev.users u on p.user_id = u.id
                    LEFT JOIN votes v on p.id = v.post_id
                    WHERE p.id = %s;""", (id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user:int = Depends(oauth2.get_current_user), db = Depends(database.get_db)):
    cursor, conn = db
    
    # Check if post exists AND get it first
    cursor.execute("""SELECT * FROM dev.posts WHERE id = %s""", (id,))
    post = cursor.fetchone()
    
    if not post:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    # Check authorization BEFORE deleting
    if post.get('user_id') != current_user.get('id'):
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform requested action.')
    
    # Now delete (safe to do)
    try:
        cursor.execute("""DELETE from dev.votes WHERE post_id = %s""", (id,))
        cursor.execute("""DELETE FROM dev.posts WHERE id = %s""", (id,))
        conn.commit()
    except:
        conn.rollback()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostBase, current_user:int = Depends(oauth2.get_current_user), db = Depends(database.get_db)):
    cursor, conn = db
    cursor.execute("""WITH updated_data AS (UPDATE dev.posts SET title = %s, content = %s, published = %s WHERE id = %s
                RETURNING title, content, published, created_at AS post_created, id AS post_id, user_id),
                votes AS (SELECT post_id, COUNT(*) AS number_votes
                    FROM dev.votes GROUP BY post_id)
                    
                SELECT json_build_object('id', u.id, 'email', u.email, 
                    'created_at',u.created_at) AS user,
                title, content, published, post_created, ud.post_id, COALESCE(number_votes, 0) AS number_votes
                FROM dev.users u
                JOIN updated_data ud
                ON u.id = ud.user_id
                LEFT JOIN votes v on ud.post_id = v.post_id;""", 
                (post.title, post.content, post.published, id))
    updated_post = cursor.fetchone()
    if not updated_post:
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    if updated_post.get('user', {}).get('id') != current_user.get('id'):
        conn.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform' \
        ' requested action.')
    conn.commit()
    return updated_post
