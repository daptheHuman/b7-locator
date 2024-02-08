import json
from config.db import SessionLocal
from models.models import Product, Rack, SampleRetained


def seed_data(json_file, model):
    # Create engine and session
    session = SessionLocal

    # Open a json file
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Seed data
    # Seed data
    for item in data:
        obj = model(**item)
        session.add(obj)

    # Commit changes
    session.commit()
    session.close()


if __name__ == "__main__":
    # Seed products
    seed_data("products.json", Product)

    # Seed racks
    seed_data("racks.json", Rack)

    # Seed samples_retained
    seed_data("samples_retained.json", SampleRetained)
