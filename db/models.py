from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    size = Column(Float, nullable=False)
    rooms = Column(Integer, nullable=False)
    gps_lat = Column(Float, nullable=False)
    gps_lon = Column(Float, nullable=False)
    floor = Column(Integer, nullable=True)  # Only for flats
    construction_year = Column(Integer, nullable=True)
    last_reconstruction_year = Column(Integer, nullable=True)
    energy_rating = Column(String, nullable=True)

    # Relationships
    listings = relationship("Listing", back_populates="property")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"))
    price = Column(Float, nullable=False)
    rent = Column(Boolean, default=False)
    contact = Column(String, nullable=True)
    description = Column(String, nullable=True)
    url = Column(String, unique=True, nullable=False)
    hash = Column(String, nullable=False)

    # Rent-specific fields
    rent_price = Column(Float, nullable=True)
    electricity_utilities = Column(Float, nullable=True)
    provision_rk = Column(Float, nullable=True)  # Usually 1x rent
    downpayment_1x = Column(Float, nullable=True)
    downpayment_2x = Column(Float, nullable=True)

    # Relationships
    property = relationship("Property", back_populates="listings")
