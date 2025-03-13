# main.py
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
from typing import List, Optional
from pydantic import BaseModel
import httpx
import jwt
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DB_URI")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SERVICE_ROLE_KEY")  # Use service role key for auth verification
SUPABASE_JWT_SECRET = os.getenv("JWT_SECRET")  # Get from Supabase dashboard

# Models
class Item(Base):
    __tablename__ = "items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    amazon_link = Column(Text, nullable=True)
    user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request/response
class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    amazon_link: Optional[str] = None

class ItemResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    amazon_link: Optional[str] = None
    user_id: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication function
async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    token = authorization.split(" ")[1]
    
    try:
        # Verify JWT token
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_signature": True}
        )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return user_id
    except jwt.PyJWTError:
        # For added security, you can also verify with Supabase directly
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{SUPABASE_URL}/auth/v1/user",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": SUPABASE_KEY
                    }
                )
                if response.status_code != 200:
                    raise HTTPException(status_code=401, detail="Invalid token")
                user_data = response.json()
                return user_data.get("id")
        except:
            raise HTTPException(status_code=401, detail="Authentication failed")

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CRUD operations
@app.post("/items/", response_model=ItemResponse)
async def create_item(
    item: ItemCreate, 
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    db_item = Item(
        name=item.name,
        description=item.description,
        amazon_link=item.amazon_link,
        user_id=user_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[ItemResponse])
async def get_items(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    items = db.query(Item).filter(Item.user_id == user_id).all()
    return items

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    item = db.query(Item).filter(Item.id == item_id, Item.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found or access denied")
    return item

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    item_update: ItemCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    db_item = db.query(Item).filter(Item.id == item_id, Item.user_id == user_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found or access denied")
    
    db_item.name = item_update.name
    db_item.description = item_update.description
    db_item.amazon_link = item_update.amazon_link
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}", response_model=dict)
async def delete_item(
    item_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user)
):
    db_item = db.query(Item).filter(Item.id == item_id, Item.user_id == user_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found or access denied")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

# Run with: uvicorn main:app --reload