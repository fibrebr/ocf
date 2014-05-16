from models.resources.xenvm import XenVM
from models.resources.virtualmachine import VirtualMachine
from models.resources.vtserver import VTServer
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from utils.base import db
from utils.choices import VirtTechClass, OSDistClass, OSVersionClass, OSTypeClass
from utils.mutexstore import MutexStore
import amsoil.core.log
import amsoil.core.pluginmanager as pm

logging=amsoil.core.log.getLogger('XenServer')

'''@author: msune, SergioVidiella'''

def validate_agent_url_wrapper():
    VTServer.validate_agent_url()

class XenServer(VTServer):
    """Virtualization Server Class."""
         
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'xenserver'
    __table_args__ = {'extend_existing':True}
    
    vtserver_ptr_id = db.Column(db.ForeignKey(table_prefix + 'vtserver.id'), primary_key=True)
    vtserver = db.relationship("VTServer", backref="xenserver")
    
    '''VMs array'''
    vms = association_proxy("xenserver_vms", "xenvm", creator=lambda vm:XenServerVMs(xenvm=vm))
    
    '''Private methods'''
    def __tupleContainsKey(tu,key):
        for val in tu:
            if val[0] == key:
                return True
        return False
    
    def __addInterface(self,interface):
        if not isinstance(interface,NetworkInterface):
            raise Exception("Cannot add an interface if is not a NetworkInterface object instance")
    
    '''Constructors'''
    @staticmethod
    def constructor(name, os_type, os_distribution, os_version, agent_url, agent_password, save=True):
        self = XenServer()
        try:
            self.set_name(name)
            self.set_virtualisation_technology(VirtTechClass.VIRT_TECH_TYPE_XEN)
            self.set_operating_system_type(os_type)
            self.set_operating_system_distribution(os_distribution)
            self.set_operating_system_version(os_version)
            self.set_agent_url(agent_url)
            self.set_agent_password(agent_password)
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
            return self
        except Exception as e:
            print e
            self.destroy()
            raise e
    
    '''Updater'''
    def updateServer(self,name,os_type,os_distribution,os_version,agent_url,agent_password,save=True):
        try:
            self.set_name(name)
            self.set_virtualisation_technology(VirtTechClass.VIRT_TECH_TYPE_XEN)
            self.set_operating_system_type(os_type)
            self.set_operating_system_distribution(os_distribution)
            self.set_operating_system_version(os_version)
            self.set_agent_url(agent_url)
            self.set_agent_password(agent_password)
            self.do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
            return self
        except Exception as e:
            print e
            self.destroy()
            raise e
    
    '''Destructor'''
    def destroy(self):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            # Destroy interfaces
            for inter in self.network_interfaces.all():
                inter.destroy()
            db.session.delete(self)
            db.session.commit()
    
    ''' Public interface methods '''
    def get_vms(self,**kwargs):
        return self.vms.filter_by(**kwargs).all()
        
    def get_vm(self,**kwargs):
        return self.vms.filter_by(**kwargs).one()
    
    def create_vm(self, name, uuid, project_id, project_name, slice_id, slice_name, os_type, os_version, os_dist, memory, disc_space_gb, number_of_cpus, callback_url, hd_setup_type, hd_origin_path, virt_setup_type,save=True):
        logging.debug("**************************** Server 1")
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            logging.debug("******************************* Server 2")
            if len(XenVM.query.filter_by(uuid=uuid).all()) > 0:
                logging.debug("*************************** Server FAIL")
                raise Exception("Cannot create a Virtual Machine with the same UUID as an existing one")
            # Allocate interfaces for the VM
            logging.debug("*************************** Server 3")
            interfaces = self.create_enslaved_vm_interfaces()
            # Call factory        
            logging.debug("**************************** Server 4")
            logging.debug("******************************** XENVM - PARAMS\nNAME => %s\nUUID => %s\nPROJECT_ID => %s\nPROJECT_NAME => %s\nSLICE_ID => %s\nSLICE_NAME => %s\nOPERATING SYSTEM TYPE => %s\nOPERATING SYSTEM VERSION => %s\nOPERATING SYSTEM DISTRIBUTION => %s\nMEMORY => %s\nDISC SPACE GB => %s\nNUMBER OF CPUS => %s\nCALLBACK URL => %s\nINTERFACES => %s\nHARD DISC SETUP TYPE => %s\nHARD DISC ORIGIN PATH => %s\nVIRTUALIZATION SETUP TYPE => %s\nSAVE => %s" % (name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,disc_space_gb,number_of_cpus,callback_url,str(interfaces),hd_setup_type,hd_origin_path,virt_setup_type, save))
            vm = XenVM.create(name,uuid,project_id,project_name,slice_id,slice_name,os_type,os_version,os_dist,memory,disc_space_gb,number_of_cpus,callback_url,interfaces,hd_setup_type,hd_origin_path,virt_setup_type,save)
            logging.debug("**************************** Server 5")
            self.vms.append(vm)        
            self.auto_save()
            logging.debug("**************************** Server 6")
            return vm

    def delete_vm(self,vm):
        with MutexStore.get_object_lock(self.get_lock_identifier()):
            if vm not in self.vms.all():
                raise Exception("Cannot delete a VM from pool if it is not already in")
            db_session.delete(vm)
            db_session.commit()
            vm.destroy()
            self.auto_save()


class XenServerVMs(db.Model):
    """Relation between Xen Virtual Machines and Xen Virtualization Server"""
    config = pm.getService("config")
    table_prefix = config.get("virtrm.DATABASE_PREFIX")
    __tablename__ = table_prefix + 'xenserver_vms'
    # Table attributes
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    xenserver_id = db.Column(db.ForeignKey(table_prefix + 'xenserver.vtserver_ptr_id'), nullable=False, index=True)
    xenvm_id = db.Column(db.ForeignKey(table_prefix + 'xenvm.virtualmachine_ptr_id'), nullable=False, index=True)
    # Relationships
    xenserver = db.relationship("XenServer", backref=db.backref("xenserver_vms", cascade="all, delete-orphan"))
    xenvm = db.relationship("XenVM", backref=db.backref("xenserver_associations", cascade="all, delete-orphan"))

