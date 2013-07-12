from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from utils.commonbase import Base

'''@author: SergioVidiella'''


class VTServerIpRange(Base):
    """Subscribed IP4 ranges to the VTServer's."""

    __tablename__ = 'vt_manager_vtserver_subscribedIp4Ranges'

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    vtserver_id = Column(Integer, ForeignKey('vt_manager_vtserver.id'))
    ip4range_id = Column(Integer, ForeignKey('vt_manager_ip4range.id'))

    server = relationship("VTServer", backref=backref("vtserver_subscribed_ip4ranges", cascade="all, delete-orphan"))
    subscribedIp4Range = relationship("Ip4Range")

