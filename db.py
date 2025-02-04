import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

load_dotenv(override=True)

# Create the SQLAlchemy engine
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

Base = declarative_base()

class SmartContractAddress(Base):
    __tablename__ = 'smart_contract_addresses'
    contract_address = Column(String, unique=True, primary_key=True, nullable=False)
    has_detail = Column(Boolean, default=False)

    details = relationship("SmartContractDetail", back_populates="contract")

class SmartContractDetail(Base):
    __tablename__ = 'smart_contract_details'
    id = Column(Integer, primary_key=True)
    contract_address = Column(String, ForeignKey('smart_contract_addresses.contract_address'), nullable=False)
    contract = relationship("SmartContractAddress", back_populates="details")
    details = Column(JSON, nullable=False)


# Create the table in the database
Base.metadata.create_all(engine)

# Function to store addresses in the database (insert if not exists)
def store_addresses_in_db(contract_addresses):
    Session = sessionmaker(bind=engine)
    session = Session()

    for address in contract_addresses:
        try:
            # Create a new SmartContract object and merge it into the session
            contract = SmartContractAddress(contract_address=address, has_detail=False)
            session.add(contract)
            session.commit()
            print(f"Successfully inserted {address} into the database.")
        except Exception as e:
            # Handle the case when the address already exists in the database
            session.rollback()
            print(f"Address {address} already exists in the database. Skipping.")
            # print(str(e))

    session.close()
    print("Database connection closed.")

def get_addresses_without_details():
    Session = sessionmaker(bind=engine)
    session = Session()

    addresses = session.query(SmartContractAddress).filter(SmartContractAddress.has_detail == False).all()
    session.close()
    return addresses

def store_details_in_db(contract_address, details):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        contract = session.query(SmartContractAddress).filter(SmartContractAddress.contract_address == contract_address).first()
        if contract is None:
            print(f"Address {contract_address} does not exist in the database. Skipping.")
            return
        contract.has_detail = True
        detail = SmartContractDetail(contract_address=contract_address, details=details)
        session.merge(detail)
        session.commit()
        session.close()
        print(f"Successfully inserted details for {contract_address} into the database.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting details for {contract_address} into the database.")
        print(str(e))
    session.close()


def get_web_data(limit=1000):
    print(f"Engine: {DATABASE_URL}")
    Session = sessionmaker(bind=engine)
    session = Session()

    contracts = session.query(SmartContractDetail.contract_address, SmartContractDetail.details['ContractName']).join(SmartContractDetail.contract).filter(SmartContractAddress.has_detail == True).order_by(SmartContractDetail.id.desc()).limit(limit).all()
    session.close()
    print(f"Found {len(contracts)} contracts.")
    return contracts

def get_details_for_address(address):
    Session = sessionmaker(bind=engine)
    session = Session()

    contract = session.query(SmartContractDetail).filter(SmartContractDetail.contract_address == address).first()
    session.close()
    if contract is None:
        return None
    return contract.details

def get_count_all():
    Session = sessionmaker(bind=engine)
    session = Session()

    count = session.query(SmartContractDetail).count()
    session.close()
    return count

if __name__ == '__main__':
    get_web_data()
