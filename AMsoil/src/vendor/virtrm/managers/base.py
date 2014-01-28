from controller.dispatchers.provisioning.query import ProvisioningDispatcher
from controller.drivers.virt import VTDriver
from datetime import datetime, timedelta
from resources.serverallocatedvms import ServerAllocatedVMs
from resources.virtualmachine import VirtualMachine
from resources.vmallocated import VMAllocated
from resources.vmexpires import VMExpires
from resources.vtserver import VTServer
from resources.xenserver import XenServer
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from utils.action import Action
from utils.base import db
from utils.expires import Expires
from utils.servicethread import ServiceThread
from utils.vmmanager import VMManager
from utils.xrn import *
import amsoil.core.log
import amsoil.core.pluginmanager as pm
import time
import utils.exceptions as virt_exception

logging=amsoil.core.log.getLogger('VTResourceManager')

'''
@author: SergioVidiella, CarolinaFernandez
'''

class VTResourceManager(object):
    config = pm.getService("config")
    worker = pm.getService("worker")
    # FIXME or REMOVE: circular dependency
    #virtrm = pm.getService("virtrm")
    #from virtrm.controller.drivers.virt import VTDriver

    # Sec in the allocated state
    RESERVATION_TIMEOUT = config.get("virtrm.MAX_RESERVATION_DURATION")
    # Sec in the provisioned state (you can always call renew)
    MAX_VM_DURATION = config.get("virtrm.MAX_VM_DURATION")
    
    EXPIRY_CHECK_INTERVAL = config.get("virtrm.EXPIRATION_VM_CHECK_INTERVAL") 
    
    ALLOCATION_STATE_ALLOCATED = "allocated"
    ALLOCATION_STATE_PROVISIONED = "provisioned"
    
    def __init__(self):
        super(VTResourceManager, self).__init__()
        # Register callback for regular updates
        self.worker.addAsReccurring("virtrm", "check_expiration_vm", None, self.EXPIRY_CHECK_INTERVAL)
    
    # Server methods
    def get_servers(self, uuid=None):
        """
        Get server by uuid. 
        If no uuid provided, return all servers.
        """
        if uuid:
            servers = self.get_server(uuid)
        else:
            servers = VTDriver.get_all_servers()
        logging.debug("**************************************" + str(servers))
        return servers
    
    def get_server(self, uuid):
        """
        Get server with a given UUID.
        """
        server = VTDriver.get_server_by_uuid(uuid)
        return server   
    
    def get_server_info(self, uuid):
        """
        Retrieve info for a server with a given UUID.
        """
        pass
    
    def get_vms_in_server(self, uuid):
        """
        Obtains list of VMs for a server with a given UUID.
        """
        pass
    
    # VM methods
    def get_vm_status(self, vm_urn, slice_name=None, project_name=None, allocation_status=False, operational_status=False, server_name=False, expiration_time=False):
        """
        Verify if the VM exists and return the status with the required params.
        """
        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        vm_status = dict()
        vm_status['name'] = vm_urn
        if not slice_name:
            slice_name = get_leaf(get_authority(vm_hrn))
        if not project_name:
            project_name = get_leaf(get_authority(get_authority(vm_hrn)))
        vm = VMAllocated.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).filter_by(project_name=project_name).first()
        if vm:
            if allocation_status:
                vm_status['allocation_status'] = self.ALLOCATION_STATE_ALLOCATED
        else:
            vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).filter_by(project_name=project_name).first().get_child_object()
            if vm:
                if allocation_status:
                    vm_status['allocation_status'] = self.ALLOCATION_STATE_PROVISIONED
                if operational_status:
                    vm_status['operational_status'] = vm.status
            else:
                raise virt_exception.VTAMVMNotFound(urn)
        if expiration_time:
            vm_status['expires'] = vm.expires.expires
        if server_name:
            vm_status['server'] = vm.get_server().name
        return vm_status

    def get_vms_in_slice(self, slice_urn):
        """
        Get all VMs in slice with given slice_urn.
        """
        vms = list()
        vms_created = self._get_provisioned_vms_in_slice(slice_urn)
        if vms_created:
            vms.extend(vms_created)
        vms_reserved = self._get_allocated_vms_in_slice(slice_urn)
        if vms_reserved:
            vms.extend(vms_reserved)
        return vms
    
    def _get_provisioned_vms_in_slice(self, slice_urn):
        """
        Get all VMs provisioned (created) in a given slice.
        """
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        project_name = get_leaf(get_authority(slice_hrn))
        vms = VirtualMachine.query.filter_by(slice_name=slice_name).filter_by(project_name=project_name).all()
        if vms:
            vms_created = list()
            for vm in vms:
                vm_hrn = get_authority(get_authority(slice_urn))+'.'+vm.project_name+'.'+vm.slice_name+'.'+ vm.name
                vm_urn = hrn_to_urn(vm_hrn, 'sliver')
                vms_created.append({'name':vm_urn, 'status':vm.status, 'expires':vm.expires.expires})
            return vms_created
        else:
            return None

    def _get_allocated_vms_in_slice(self, slice_urn):
        """
        Get all VMs allocated (reserved) in a given slice.
        """
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        project_name = get_leaf(get_authority(slice_hrn))
        vms = VMAllocated.query.filter_by(slice_name=slice_name).filter_by(project_name=project_name).all()
        if vms:
            vms_created = list()
            for vm in vms:
                vm_hrn = get_authority(get_authority(slice_hrn))+'.'+vm.project_name+'.'+vm.slice_name+'.'+ vm.name
                vm_urn = hrn_to_urn(vm_hrn, 'sliver')
                vms_created.append({'name':vm_urn, 'expires':vm.expires.expires, 'status':self.ALLOCATION_STATUS_ALLOCATED})
            return vms_created
        else:
            return None
    
    def _destroy_vm(self, vm_id, server_uuid):
        if not server_uuid:
            server_uuid = XenDriver.get_server_uuid_by_vm_id(vm_id)
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_DELETE_TYPE)
            return "success"
        except Exception as e:
            return "error" 
    
    # FIXME: use Translator.{VMdictToClass, VMdicIfacesToClass} for this!
    def _vm_dict_to_class(self, requested_vm, slice_name, end_time):
        vm = VMAllocated()
        vm.name = requested_vm['name']
        vm.memory = int(requested_vm['memory_mb'])
        vm.disc_space_gb = float(requested_vm['hd_size_mb'])/1024
        vm.project_name = requested_vm['project_name']
        vm.slice_id = 0 #necessary?
        vm.slice_name = slice_name
        vm.operating_system_type = requested_vm['operating_system_type'] 
        vm.operating_system_version = requested_vm['operating_system_version']
        vm.operating_system_distribution = requested_vm['operating_system_distribution']
        vm.hypervisor = requested_vm['hypervisor']
        vm.hd_setup_type = requested_vm['hd_setup_type']
        vm.hd_origin_path = requested_vm['hd_origin_path']
        vm.virtualization_setup_type = requested_vm['virtualization_setup_type']
        vm.server = VTServer.query.filter_by(name=requested_vm['server_name']).one()
        logging.debug("********************************* OK OK")
        return vm
    
    def provision_allocated_vms(self, slice_urn, end_time):
        """
        Provision (create) previously allocated (reserved) VMs.
        """
        import uuid
        max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None:
            end_time = max_end_time
        if (end_time > max_end_time):
            raise VTMaxVMDurationExceeded(vm_name)
        if (end_time < datetime.utcnow()):
            end_time = max_end_time
        allocated_vms = VMAllocated.query.filter_by(slice_name=get_leaf(slice_urn)).all()        
        vms_params = list()
        servers = list()
        project = None
        for allocated_vm in allocated_vms:
            server = VTDriver.get_server_by_id(allocated_vm.get_server_id())
            params = dict()
            params['name'] = allocated_vm.name
            params['uuid'] = uuid.uuid4()
            params['state'] = "creating"
            params['project-id'] = None
            params['server-id'] = server.uuid
            params['slice-id'] = allocated_vm.sliceId
            params['slice-name'] = allocated_vm.slice_name
            params['operating-system-type'] = allocated_vm.operatingSystemType
            params['operating-system-version'] = allocated_vm.operatingSystemVersion
            params['operating-system-distribution'] = allocated_vm.operatingSystemDistribution
            params['virtualization-type'] = allocated_vm.hypervisor
            params['hd-setup-type'] = allocated_vm.hdSetupType
            params['hd-origin-path'] = allocated_vm.hdOriginPath
            params['virtualization-setup-type'] = allocated_vm.virtualizationSetupType
            params['memory-mb'] = allocated_vm.memory
            #XXX: Currently, this is always an empty list, interfaces are not allowed
            interfaces = list()
            interface = dict()
            interface['gw'] = None
            interface['mac'] = None
            interface['name'] = None
            interface['dns1'] = None
            interface['dns2'] = None
            interface['ip'] = None
            interface['mask'] = None
            interfaces.append(interface) 
            #for allocated_interface in allocated_vm.interfaces:
            #        interface = dict()
            #        interface['gw'] = allocated_interface.gw
            #        interface['mac'] = allocated_interface.mac
            #        interface['name'] = allocated_interface.name
            #        interface['dns1'] = allocated_interface.dns1
            #        interface['dns2'] = allocated_interface.dns2
            #        interface['ip'] = allocated_interface.ip
            #        interface['mask'] = allocated_interface.mask
            #        interfaces.append(interface)
            params['interfaces'] = interfaces
            if not project:
                project = params['project-id']
            if not server.uuid in servers:
                servers.append(server.uuid)
                new_server = dict()
                new_server['component_id'] = server.uuid 
                new_server['slivers'] = list()
                new_server['slivers'].append(params)
                vms_params.append(new_server)
            else:
                for vm_server in vms_params:
                    if vm_server['component_id'] is server.uuid:
                        vm_server['slivers'].append(params)
        if vms_params:
            created_vms = self._provision_vms(vms_params, slice_urn, project)
        else:
            raise virt_exception.VTAMNoSliversInSlice(slice_urn)
        for key in created_vms.keys():
            for created_vm in created_vms[key]:
                vm_hrn, hrn_type = urn_to_hrn(created_vm['name'])
                vm_name = get_leaf(vm_hrn)
                slice_name = get_leaf(get_authority(vm_hrn))
                vm = VMAllocated.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first()
                current_vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first().get_child_object()
                time.sleep(10)
                #XXX: Very ugly, improve this
                if not current_vm:
                    time.sleep(10)
                    current_vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first().get_child_object()
                if current_vm:
                    db.session.delete(vm)
                    db.session.commit()
                    vm_expires = Expires()
                    vm_expires.expires = end_time
                    vm_expires.vm_id = current_vm.id
                    created_vm['expires'] = end_time 
                    db.session.add(vm_expires)
                    db.session.commit()
                else:
                    created_vm['expires'] = vm.expires
                    created_vm['error'] = 'VM cannot be created'
        return created_vms
        
    def _provision_vms(self, vm_params, slice_urn, project_name):
        """
        Provision (create) VMs.
        """
        created_vms = list()
        slice_hrn, urn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        provisioning_rspecs, actions = VMManager.get_action_instance(vm_params,project_name,slice_name)
        vm_results = dict()
        for provisioning_rspec, action in zip(provisioning_rspecs, actions):
            ServiceThread.start_method_in_new_thread(ProvisioningDispatcher.process, provisioning_rspec, 'SFA.OCF.VTM')
            vm = provisioning_rspec.action[0].server.virtual_machines[0]
            vm_hrn = 'geni.gpo.gcf.' + vm.slice_name + '.' + vm.name
            vm_urn = hrn_to_urn(vm_hrn, 'sliver')
            server = VTDriver.get_server_by_uuid(vm.server_id)
            if server.name not in vm_results.keys():
                vm_results[server.name] = list()
            vm_results[server.name].append({'name':vm_urn, 'status':'ongoing'})
        return vm_results
    
    # VM status methods
    def start_vm(self, vm_urn):
        vm_hrn, type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).first().get_child_object()
        expiration = Expires.query.get(vm.id).expires
        vm_id = vm.id
        status = vm.status
        #FIXME: This should not be done that way
        xen_vm = db_session.query(XenVM).filter(XenVM.virtualmachine_ptr_id == vm_id).first()
        server = xen_vm.xenserver_associations
        server_uuid = server.uuid
        db_session.expunge_all()
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm_id, server_uuid, Action.PROVISIONING_VM_START_TYPE)
            return {'name':vm_urn, 'status':status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':status, 'expires':expiration, 'error': 'Could not start the VM'}
    
    def pause_vm(self, vm_urn):
        """
        Stores VM status in memory.
        Xen: xm pause <my_vm>
        See http://stackoverflow.com/questions/11438922/how-does-xen-pause-a-vm
        """
        pass
    
    def stop_vm(self, vm_urn=None, vm_name=None, slice_name=None):
        if vm_urn and not (vm_name and slice_name):
            vm_hrn, type = urn_to_hrn(vm_urn)
            vm_name = get_leaf(vm_hrn)
            slice_name = get_leaf(get_authority(vm_hrn))
            vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).one().get_child_object()
            expiration = Expires.query.get(vm.id).one().expires
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm.id, vm.xenserver.uuid, Action.PROVISIONING_VM_STOP_TYPE)
            return {'name':vm_urn, 'status':vm.status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':vm.status, 'expires':expiration, 'error': 'Could not stop the VM'}
    
    def restart_vm(self, vm_urn):
        vm_hrn, type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        vm = VirtualMachine.query.filter_by(name=vm_name).filter_by(slice_name=slice_name).one().get_child_object()
        expiration = Expires.query.get(vm.id).one().expires
        try:
            VTDriver.propagate_action_to_provisioning_dispatcher(vm.id, vm.xenserver.uuid, Action.PROVISIONING_VM_REBOOT_TYPE)
            return {'name':vm_urn, 'status':vm.status, 'expires':expiration}
        except Exception as e:
            return {'name':vm_urn, 'status':vm.status, 'expires':expiration, 'error': 'Could not Restart the VM'}
    
    def delete_vm(self, vm_urn, slice_name=None):
        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        if not slice_name:
            slice_name = get_leaf(get_authority(vm_hrn))
        vm_name = get_leaf(vm_hrn)
        vm = db_session.query(VirtualMachine).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.slice_name == slice_name).first()
        if vm != None:
             db_session.expunge(vm)
             deleted_vm = self._destroy_vm_with_expiration(vm.id)
        else:
             vm = db_session.query(VMAllocated).filter(VMAllocated.name == vm_name).first()
             if vm != None:
                db_session.expunge(vm)
                deleted_vm = self._unallocate_vm(vm.id)
                if not deleted_vm:
                    deleted_vm = dict()
                    deleted_vm = dict()
                    deleted_vm['name'] = vm_urn
                    deleted_vm['expires'] = None
                    deleted_vm['error'] = "The requested VM does not exist, it may have expired"
             else:
                deleted_vm = dict()
                deleted_vm['name'] = vm_urn
                deleted_vm['expires'] = None
                deleted_vm['error'] = "The requested VM does not exist, it may have expired"
        return deleted_vm
    
    # Slice methods
    def add_vm_to_slice(self, slice_urn, vm_urn):
        """
        Add VM to slive with given URN.
        """
        pass
    
    def remove_vm_to_slice(self, slice_urn, vm_urn):
        """
        Remove VM from slive with given URN.
        """
        pass
    
    # XXX Check
    def start_vms_in_slice(self, slice_urn):
        slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        started_vms = list()
        for vm in vms:
            started_vms.append(self.start_vm(None, vm.name, vm.slice_name))
        db_session.expunge_all()
        return started_vms
    
    def stop_vms_in_slice(self, slice_urn):
        slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        stopped_vms = list()
        for vm in vms:
            stopped_vms.append(self.stop_vm(None, vm.name, vm.slice_name))
        db_session.expunge_all()
        return stopped_vms
    
    # XXX Check
    def restart_vms_in_slice(self, slice_urn):
        slice_name = get_leaf(urn_to_hrn(slice_urn)[0])
        vms = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        restarted_vms = list()
        for vm in vms:
            restarted_vms.append(self.restart_vm(None, vm.name, vm.slice_name))
        db_session.expunge_all()
        return restarted_vms
    
    def delete_vms_in_slice(self, slice_urn):
        slice_hrn, hrn_type = urn_to_hrn(slice_urn)
        slice_name = get_leaf(slice_hrn)
        # get all the vms from the given slice and delete them
        vms = list()
        vms_created = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).all()
        if vms_created:
            vms.extend(vms_created)
        vms_allocated = db_session.query(VMAllocated).filter(VMAllocated.slice_name == slice_name).all()
        if vms_allocated:
            vms.extend(vms_allocated)
        if not vms:
            raise virt_exception.VTAMNoVMsInSlice(slice_name)
        deleted_vms = list()        
        for vm in vms:
            vm_hrn = 'geni.gpo.gcf.' + slice_name + '.' + vm.name
            vm_urn = hrn_to_urn(vm_hrn, 'sliver')
            deleted_vm = self.delete_vm(vm_urn, slice_name)
            deleted_vms.append(deleted_vm)
        db_session.expunge_all()
        return deleted_vms
    
    # Allocation & expiration methods
    def _check_reservation_time(self, end_time):
        max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if end_time == None or end_time < datetime.utcnow():
            return max_end_time
        elif (end_time > max_end_time):
            raise VTMaxVMDurationExceeded(vm_name)
        else:
            return end_time
    
    def allocate_vm(self, vm, slice_name, end_time):
        """
        Allocate a VM in the given slice.
        """
        # Check if the VM name already exists, as a created VM or an allocated VM
        if VirtualMachine.query.filter_by(name=vm['name']).filter_by(slice_name=slice_name).filter_by(project_name=vm['project_name']).first() != None or VMAllocated.query.filter_by(name=vm['name']).filter_by(slice_name=slice_name).filter_by(project_name=vm['project_name']).first() != None:
            raise virt_exception.VTAMVmNameAlreadyTaken(vm['name'])
        # Check if the server is one of the given servers
        # FIXME: Filter should be done by UUID, not by name
        if VTServer.query.filter_by(name=vm['server_name']).first() == None:
            raise virt_exception.VTAMServerNotFound(vm['server_name'])
        try:
            expiration_time = self._check_reservation_time(end_time)
        except Exception as e:
            raise e
        # Once we know all the VMs could be created, we start reserving them
        expires = Expires.constructor(expiration_time, False)
        logging.debug("**************************************** OK")
        vm_allocated_model = self._vm_dict_to_class(vm, slice_name, expiration_time)
        logging.debug("***********************************" + str(expires.id))
        vm_allocated_model.expires = expires
        db.session.add(vm_allocated_model)
        db.session.commit()
        server = VTDriver.get_server_by_id(vm_allocated_model.server_id)
        logging.debug("********************************" +  str(server.allocated_vms))
        return vm_allocated_model, server
        
    #XXX: continue from this point
    def set_vm_expiration(self, vm_urn, status, expiration_time):
        vm_hrn, hrn_type = urn_to_hrn(vm_urn)
        vm_name = get_leaf(vm_hrn)
        slice_name = get_leaf(get_authority(vm_hrn))
        project_name = get_leaf(get_authority(get_authority(vm_hrn)))
        max_duration = self.RESERVATION_TIMEOUT
        max_end_time = datetime.utcnow() + timedelta(0, max_duration)
        if (status == "allocated"):
            vm_expires = db_session.query(VMAllocated).filter(VMAllocated.slice_name == slice_name).filter(VMAllocated.name == vm_name).filter(VMAllocated.project_name == project_name).one()
            vm_state = "allocated"
        else:
            vm = db_session.query(VirtualMachine).filter(VirtualMachine.slice_name == slice_name).filter(VirtualMachine.name == vm_name).filter(VirtualMachine.project_name == project_name).one()
            vm_state = vm.state
            db_session.expunge(vm)
            vm_expires = db_session.query(Expires).filter(Expires.vm_id == vm.id).first()
        if (expiration_time > max_end_time):
            db_sesion.expunge_all()
            raise VTMaxVMDurationExceeded(vm_name, vm_expires.expires)
        last_expiration = vm_expires.expires
        vm_expires.expires = expiration_time
        vm_hrn = get_leaf(get_authority(get_authority(get_authority(vm_hrn)))) + '.' + vm.project_name + '.' + vm.slice_name + '.' + vm.name
        vm_urn = hrn_to_urn(vm_hrn, 'sliver')
        db_session.add(vm_expires)
        db_session.commit()
        db_session.expunge(vm_expires)
        return {'name':vm_urn, 'expires':expiration_time, 'status':vm_state}, last_expiration
    
    def _unallocate_vm(self, vm_id):
        """
        Delete the entry in the table of allocated VMs.
        """
        vm = VMAllocated.query.get(vm_id)
        deleted_vm = dict()
        deleted_vm['name'] = vm.name
        deleted_vm['expires'] = vm.expires
        vm.destroy()
        return deleted_vm
    
    # Authority methods
    def get_vms_in_authority(self, authority_urn):
        """
        Get list of VMs in authority with given URN.
        """
        pass
    
    def get_allocated_vms_in_authority(self, authority_urn):
        """
        Get list of allocated (reserved) VMs in authority with given URN.
        """
        pass
    
    def get_provisioned_vms_in_authority(self, authority_urn):
        """
        Get list of provisioned (created) VMs in authority with given URN.
        """
        pass
    
    @worker.outsideprocess
    def check_expiration_vm(self, params):
        """
        Checks expiration for both allocated and provisioned VMs
        and deletes accordingly, either from DB or disk.
        """
        expirations = Expires.query.filter(Expires.expires < datetime.utcnow()).all()
        for expiration in expirations:
            if expiration.get_vm():
                if isinstance(expiration.get_vm(), VMAllocated):
                    self._unallocate_vm(expiration.get_vm().id)
                elif isinstance(expiration.get_vm(), VirtualMachine):
                    self._destroy_vm_with_expiration(expiration.get_vm()._id)
                else:
                    db.session.delete(expiration)
                    db.session.commit()
            else:
                db.session.delete(expiration)
                db.session.commit()
        return
    
    # Backup & migration methods
    # XXX Do not implement right now
    def copy_vm_to_slice(self, slice_urn, vm_urn):
        pass
    
    def move_vm_to_slice(self, slice_urn, vm_urn):
        pass
    
    def copy_vm_to_server(self, server_urn, vm_urn):
        pass
    
    def move_vm_to_server(self, server_urn, vm_urn):
        pass
    
    def update_template_to_server(self, server_urn, template_path):
        pass
    
    def get_vm_snapshot(self, server_urn, template_name):
        pass

