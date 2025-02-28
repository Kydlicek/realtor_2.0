from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from elasticsearch import Elasticsearch
from datetime import datetime
import os

# Database connection
# DATABASE_URI = os.getenv("DATABASE_URI")
DATABASE_URI = 'postgresql://admin:Admin1234@postgres:5432/real_estate'
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
def check_link_exists(url):
    """
    Check if a listing URL already exists in the database.
    Returns:
        - True if the URL exists.
        - False if the URL does not exist or an error occurs.
    """
    return False
    try:
        existing_listing = session.execute(
            listings.select().where(listings.c.url == url)
        ).fetchone()
        return (
            existing_listing is not None
        )  # Returns True if URL exists, False otherwise
    except Exception as e:
        print(f"Error checking link: {e}")
        return False  # Returns False if an error occurs
    


# Function to save property
def save_property(property_data):
    """
    Save property data to PostgreSQL.
    """
    print(f'save property recieved {property_data}')
    return True
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
    print(f'save listing recieved {listing_data}')
    return True
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
            "date_created": (
                listing.date_created.isoformat() if listing.date_created else None
            ),
            "date_removed": (
                listing.date_removed.isoformat() if listing.date_removed else None
            ),
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
            "garage_count": property_data.garage_count,
        }

        # Index the document in Elasticsearch
        es.index(index="property_listings", id=listing.id, body=doc)
        print(f"Synced listing {listing.id} to Elasticsearch!")
    except Exception as e:
        print(f"Error syncing to Elasticsearch: {e}")



    # # Step 1: Check if the listing URL already exists
    # if check_link_exists(listing_data["url"]):
    #     print("Listing already exists in the database. Skipping...")
    # else:
    #     # Step 2: Save property
    #     property_id = save_property(property_data)
    #     if property_id:
    #         print(f"Saved property with ID: {property_id}")

    #         # Step 3: Save listing (link it to the property)
    #         listing_data["property_id"] = property_id
    #         listing_id = save_listing(listing_data)
    #         if listing_id:
    #             print(f"Saved listing with ID: {listing_id}")

    #             # Step 4: Sync to Elasticsearch
    #             sync_to_elasticsearch(listing_id)
