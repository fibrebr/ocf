from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from utils.commonbase import Base


'''@author: SergioVidiella'''


class Ip4RangeIps(Base):
    """Relation between Ip's and IpRange"""

    __tablename__ = 'vt_manager_ip4range_ips'
   
    id = Column(Integer, autoincrement=True, nullable=False,primary_key=True)
    ip4slot_id = Column(Integer, ForeignKey('vt_manager_ip4slot.id'))
    ip4range_id = Column(Integer, ForeignKey('vt_manager_ip4range.id'))

    ip4slot = relationship("Ip4Slot")
