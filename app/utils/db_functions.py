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