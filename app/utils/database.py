from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from elasticsearch import Elasticsearch
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Database connection
DATABASE_URI = os.getenv("DATABASE_URI")
engine = create_engine(DATABASE_URI)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

# Elasticsearch connection
es = Elasticsearch("http://elasticsearch:9200")

# Define tables (reflect existing tables)
properties = Table("properties", metadata, autoload_with=engine)
listings = Table("listings", metadata, autoload_with=engine)

# Function to check if a listing URL already exists
def check_link(url):
    """
    Check if a listing URL already exists in the database.
    Returns:
        - True if the URL exists.
        - False if the URL does not exist or an error occurs.
    """
    try:
        existing_listing = session.execute(
            listings.select().where(listings.c.url == url)
        ).fetchone()
        return existing_listing is not None  # Returns True if URL exists, False otherwise
    except Exception as e:
        print(f"Error checking link: {e}")
        return False  # Returns False if an error occurs

# Function to save property
def save_property(property_data):
    """
    Save property data to PostgreSQL.
    """
    try:
        result = session.execute(properties.insert().values(**property_data))
        session.commit()
        return result.inserted_primary_key[0]  # Return the ID of the inserted property
    except Exception as e:
        session.rollback()
        print(f"Error saving property: {e}")
        return None

# Function to save listing
def save_listing(listing_data):
    """
    Save listing data to PostgreSQL.
    """
    try:
        result = session.execute(listings.insert().values(**listing_data))
        session.commit()
        return result.inserted_primary_key[0]  # Return the ID of the inserted listing
    except Exception as e:
        session.rollback()
        print(f"Error saving listing: {e}")
        return None

# Function to sync data to Elasticsearch
def sync_to_elasticsearch(listing_id):
    """
    Sync listing data to Elasticsearch.
    """
    try:
        # Fetch the listing and property data
        listing = session.execute(
            listings.select().where(listings.c.id == listing_id)
        ).fetchone()
        property_data = session.execute(
            properties.select().where(properties.c.id == listing.property_id)
        ).fetchone()

        # Prepare the document for Elasticsearch
        doc = {
            "id": listing.id,
            "source": listing.source,
            "external_id": listing.external_id,
            "url": listing.url,
            "price": listing.price,
            "rent": listing.rent,
            "contact": listing.contact,
            "description": listing.description,
            "hash": listing.hash,
            "date_created": listing.date_created.isoformat() if listing.date_created else None,
            "date_removed": listing.date_removed.isoformat() if listing.date_removed else None,
            "is_active": listing.is_active,
            "property_type": property_data.property_type,
            "size": property_data.size,
            "rooms": property_data.rooms,
            "gps_lat": property_data.gps_lat,
            "gps_lon": property_data.gps_lon,
            "construction_year": property_data.construction_year,
            "last_reconstruction_year": property_data.last_reconstruction_year,
            "energy_rating": property_data.energy_rating,
            "has_balcony": property_data.has_balcony,
            "has_parking": property_data.has_parking,
            "condition": property_data.condition,
            "floor": property_data.floor,
            "building_floors": property_data.building_floors,
            "elevator": property_data.elevator,
            "garden_size_m2": property_data.garden_size_m2,
            "garage_count": property_data.garage_count
        }

        # Index the document in Elasticsearch
        es.index(index="property_listings", id=listing.id, body=doc)
        print(f"Synced listing {listing.id} to Elasticsearch!")
    except Exception as e:
        print(f"Error syncing to Elasticsearch: {e}")

# Example usage
if __name__ == "__main__":
    # Example property data
    property_data = {
        "property_type": "flat",
        "size": 80.5,
        "rooms": 3,
        "gps_lat": 50.0755,
        "gps_lon": 14.4378,
        "construction_year": 2005,
        "last_reconstruction_year": 2015,
        "energy_rating": "B",
        "has_balcony": True,
        "has_parking": True,
        "condition": "renovated",
        "floor": 2,
        "building_floors": 5,
        "elevator": True,
        "garden_size_m2": None,
        "garage_count": 1
    }

    # Example listing data
    listing_data = {
        "property_id": None,  # Will be set after saving the property
        "source": "sreality.cz",
        "external_id": "12345",
        "url": "https://sreality.cz/flat/12345",
        "price": 250000,
        "rent": False,
        "contact": "jan.novak@example.com",
        "description": "Beautiful 3-room flat in Prague.",
        "hash": "abc123",
        "date_created": datetime.utcnow(),
        "date_removed": None,
        "is_active": True,
        "rent_price": None,
        "electricity_utilities": None,
        "provision_rk": None,
        "downpayment_1x": None,
        "downpayment_2x": None
    }

    # Step 1: Check if the listing URL already exists
    if check_link(listing_data["url"]):
        print("Listing already exists in the database. Skipping...")
    else:
        # Step 2: Save property
        property_id = save_property(property_data)
        if property_id:
            print(f"Saved property with ID: {property_id}")

            # Step 3: Save listing (link it to the property)
            listing_data["property_id"] = property_id
            listing_id = save_listing(listing_data)
            if listing_id:
                print(f"Saved listing with ID: {listing_id}")

                # Step 4: Sync to Elasticsearch
                sync_to_elasticsearch(listing_id)