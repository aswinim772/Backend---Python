from database import Base
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey,Float


class Results(Base):
    __tablename__ = 'results'

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True)
    city = Column(String)
    address = Column(String)
    pincode = Column(Integer)
    country = Column(String)
    passed = Column(String)
    sat_score = Column(Integer)
