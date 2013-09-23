from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy.orm import validates

from utils import validators
from utils.commonbase import Base

from resources.macslot import MacSlot
from resources.ip4slot import Ip4Slot
from interfaces.networkinterfaceip4s import NetworkInterfaceIp4s
from interfaces.networkinterfaceconnectedto import NetworkInterfaceConnectedTo


'''@author: SergioVidiella'''


class NetworkInterface(Base):
    """Network interface model."""

    __tablename__ = 'vt_manager_networkinterface'

    '''Generic parameters'''
    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    name = Column(String(128), nullable=False)
    mac_id = Column(Integer, ForeignKey('vt_manager_macslot.id'))
    mac = relationship("MacSlot", backref='networkinterface_macs')
    ip4s = relationship("NetworkInterfaceIp4s", primaryjoin="NetworkInterfaceIp4s.networkinterface_id==NetworkInterface.id", backref="networkinterface_ips")
    isMgmt = Column(TINYINT(1), nullable=False)
    isBridge = Column(TINYINT(1), nullable=False)

    '''Interfaces connectivy'''
    connectedTo = relationship("NetworkInterfaceConnectedTo", primaryjoin="NetworkInterfaceConnectedTo.from_networkinterface_id==NetworkInterface.id", backref="from_networkinterface")

    '''Physical connection details for bridged interfaces''' 
    switchID = Column(String(23))
    port = Column(Integer)
    idForm = Column(Integer)

    '''Interface constructor '''
    @staticmethod
    def constructor(name, macStr, macObj, switchID, port, ip4Obj, isMgmt=False, isBridge=False):
	self = NetworkInterface()
	try:
            self.name = name
	    if macObj == None:
            	self.mac = MacSlot.macFactory(None,macStr)
            else:
            	if not isinstance(macObj,MacSlot):
                    raise Exception("Cannot construct NetworkInterface with a non MacSlot object as parameter")
            	self.mac = macObj
            self.isMgmt = isMgmt
            '''Connectivity'''
            if isBridge:
            	self.isBridge = isBridge
                self.switchID = switchID
                self.port = port
            if not ip4Obj == None:
                if not isinstance(ip4Obj,Ip4Slot):
                    raise Exception("Cannot construct NetworkInterface with a non Ip4Slot object as parameter")
		else:
                    self.ip4s.append(ip4Obj)
	except Exception as e:
            raise e
	return self

    def update(self, name, macStr, switchID, port):
    	try:
            self.name = name
            self.setMacStr(macStr)
            self.switchID = switchID
            self.port = port
        except Exception as e:
            raise e

    def setMacStr(self, macStr):
	self.mac.setMac(macStr)

    '''Validators'''
    @validates('name')
    def validate_name(self, key, name):
        try:
	    validators.resource_name_validator(name)
	    return name
	except Exception as e:
            raise e

    @validates('mac')
    def validate_mac(self, key, mac):
	try:
	    validators.mac_validator(mac)
	    return mac
	except Exception as e:
	    raise e

    @validates('switchID')
    def validate_switchID(self, key, switchID):
	try:
	    validators.datapath_validator(switchID)
	    return switchID
	except Exception as e:
	    raise e

    @validates('port')
    def validate_port(self, key, port):
	try:
	    validators.number_validator(port)
	    return port
	except Exception as e:
	    raise e
    
    '''Server interface factories'''
    @staticmethod
    def createServerDataBridge(name, macStr, switchID, port):
        return NetworkInterface.constructor(name, macStr, None, switchID, port, None, False, True)

    @staticmethod
    def updateServerDataBridge(name, macStr, switchID, port):
        return NetworkInterface.update(name, macStr, switchID, port)

    @staticmethod
    def createServerMgmtBridge(name, macStr):
        return NetworkInterface.constructor(name, macStr, None, None, None, None, True, True)

    '''VM interface factories'''
    @staticmethod
    def createVMDataInterface(name, macObj):
        return NetworkInterface.constructor(name, None, macObj, None, None, None, False, False)

    @staticmethod
    def createVMMgmtInterface(name, macObj, ip4):
        return NetworkInterface.constructor(name, None, macObj, None, None, ip4, True, False)
    