from utils.action import Action
from utils.xmlhelper import XmlHelper
import uuid, copy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from utils.commonbase import ENGINE


class ActionController():

	db_engine = create_engine(ENGINE, pool_recycle=6000)
	db_session_factory = sessionmaker(autoflush=True, autocommit=True, bind=db_engine, expire_on_commit=False)
	db_session = scoped_session(db_session_factory)

	@staticmethod
	def getAction(uuid):
		actions = db_session.query(Action).filter(Action.uuid==uuid).all()
		print actions
		if actions.count() ==  1:
			return actions[0]
		elif actions.count() == 0:
			raise Exception("Action with uuid %s does not exist" % uuid)
		elif actions.count() > 1:
			raise Exception("More than one Action with uuid %s" % uuid)
	
	
	@staticmethod
	def createNewAction(aType,status,objectUUID=None,description=""):
		return Action.constructor(aType,status,objectUUID,description)	

	@staticmethod
	def completeActionRspec(action, actionModel):
		action.type_ = actionModel.getType()
		#tempVMclass = XmlHelper.getProcessingResponse('dummy', None , 'dummy').response.provisioning.action[0].server.virtual_machines[0]
		#tempVMclass.uuid = actionModel.getObjectUUID()
		#action.server.virtual_machines[0] = tempVMclass
		action.server.virtual_machines[0].uuid = actionModel.getObjectUUID()

	#XXX: Why are these two functions here? Do not beling to the Action, aren't they?

	@staticmethod
	def PopulateNewActionWithVM(action, vm):
		action.id = uuid.uuid4()
		virtual_machine = action.server.virtual_machines[0]
		virtual_machine.name = vm.getName()
		virtual_machine.uuid = vm.getUUID()
		virtual_machine.project_id = vm.getProjectId()
		virtual_machine.slice_id = vm.getSliceId()
		virtual_machine.project_name = vm.getProjectName()
		virtual_machine.slice_name = vm.getSliceName()
		virtual_machine.xen_configuration.hd_setup_type = vm.getHdSetupType()

	@staticmethod
	def PopulateNetworkingParams(actionIfaces, vm):
		baseIface = copy.deepcopy(actionIfaces[0])
		actionIfaces.pop()
		#for index, vmIface in enumerate(vm.networkInterfaces.all().order_by('-isMgmt','id')):
		for index, vmIface in enumerate(vm.getNetworkInterfaces()):
			currentIface = copy.deepcopy(baseIface)
			currentIface.ismgmt = vmIface.isMgmt
			currentIface.name = "eth"+str(index)
			currentIface.mac = vmIface.mac.mac
			#XXX: ip4s are many, but xml only accepts one
			if vmIface.ip4s.all():
				currentIface.ip = vmIface.ip4s.all()[0].ip
				currentIface.mask = vmIface.ip4s.all()[0].Ip4Range.get().netMask
				currentIface.gw = vmIface.ip4s.all()[0].Ip4Range.get().gw
				currentIface.dns1 = vmIface.ip4s.all()[0].Ip4Range.get().dns1
				currentIface.dns2 = vmIface.ip4s.all()[0].Ip4Range.get().dns2
			currentIface.switch_id = vmIface.serverBridge.all()[0].name
			actionIfaces.append(currentIface)
		
	@staticmethod
	def ActionToModel(action, hyperaction, save = "noSave" ):
		actionModel = Action()
		actionModel.hyperaction = hyperaction
		if not action.status:
			actionModel.status = 'QUEUED'
		else:
			actionModel.status = action.status
		actionModel.type = action.type_
		actionModel.uuid = action.id
		return actionModel						


