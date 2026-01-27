from .database import db

def init_db():
    db.init_db()

if __name__ == "__main__":
    init_db()
