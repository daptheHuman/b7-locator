import json

from config.db import SessionLocal
from models.models import Product, Rack, SampleReferenced, SampleRetained


def seed_data(json_file, model):
    # Create engine and session
    session = SessionLocal()

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
    seed_data("data_seeding/products.json", Product)

    # Seed racks
    seed_data("data_seeding/racks.json", Rack)

    # Seed samples_retained
    seed_data("data_seeding/samples_retained.json", SampleRetained)

    # Seed samples_reference
    seed_data("data_seeding/samples_referenced.json", SampleReferenced)
