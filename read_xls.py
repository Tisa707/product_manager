import pandas as pd
from database import SessionLocal
from models import Product
from sqlalchemy.orm import Session

def import_excel(file_path: str):
    df = pd.read_excel(file_path)

    db: Session = SessionLocal()

    for _, row in df.iterrows():
        product = Product(name=row['name'], description=row['description'])
        db.add(product)

    db.commit()
    db.close()

if __name__ == "__main__":
    import_excel("your_excel_file.xlsx")
