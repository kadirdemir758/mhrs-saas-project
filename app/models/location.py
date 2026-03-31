from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Province(Base):
    """ Türkiye'nin 81 İli """
    __tablename__ = "provinces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    districts = relationship("District", back_populates="province")


class District(Base):
    """ İllere bağlı ilçeler """
    __tablename__ = "districts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    province_id = Column(Integer, ForeignKey("provinces.id", ondelete="CASCADE"), nullable=False)
    
    province = relationship("Province", back_populates="districts")
