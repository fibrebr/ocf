import shlex, subprocess
from StringIO import StringIO
from django.db import models
from django.db.models.fields import IPAddressField
import paramiko
from paramiko.rsakey import RSAKey
from expedient.clearinghouse.aggregate.models import Aggregate
from expedient.clearinghouse.resources.models import Resource, Sliver
from expedient.common.utils.modelfields import LimitedIntegerField
from expedient.common.middleware import threadlocals
from expedient.clearinghouse.utils import post_message_to_current_user
from expedient.common.messaging.models import DatedMessage
from expedient.clearinghouse.slice.models import Slice
from vt_manager.communication.utils.XmlUtils import XmlHelper 
#from vt_manager.models import Action, VTServer
from vt_plugin.models import *


class VTServer(Resource):

    '''
    Virtualization Server class
    '''
    
    class Meta:
        """Meta Class for your model."""
        app_label = 'vt_plugin'

    #From Machine
   # uuid = models.CharField(max_length = 1024, default="", editable = False)
    #name = models.CharField(max_length = 1024, default="", verbose_name = "Name")
    memory = models.IntegerField(blank = True, null=True,editable = False)
    #url = models.URLField(verify_exists = False, verbose_name = "Url of the Server")
    virtTech = models.CharField(max_length = 1024, default="", verbose_name = "Virtualization Technology")    
    vms = models.ManyToManyField('VM', blank = True, null = True, editable = False)
    freeDiscSpace = models.IntegerField(blank = True, null=True, editable = False)
    freeMemory = models.IntegerField(blank = True, null=True, editable = False)
    freeCpu = models.DecimalField(max_digits=3, decimal_places=2,blank = True, null=True, editable = False)
    operatingSystemType = models.CharField(max_length = 512, verbose_name = "OS Type")
    operatingSystemVersion = models.CharField(max_length = 512, verbose_name = "OS Version")
    operatingSystemDistribution = models.CharField(max_length = 512, verbose_name = "OS Distribution") 
    
    #aggregate_id = models.IntegerField()


    '''
    def setAggID(self, aggID):
        self.aggregate_id = aggID

    def getAggID(self):
        return self.aggregate_id
    '''
    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setUUID(self, uuid):
        self.uuid = uuid

    def getUUID(self):
        return self.uuid
    
    def setMemory(self,memory):
        if not memory in range(1,4000):
            handleFault(ExceptionMemory,memory)
            return
        else:
            self.memory = memory

    def getMemory(self):
        return self.memory


    def setVirtTech(self, virtTech):
         self.virtTech = virtTech

    def getVirtTech(self):
        return self.virtTech

    def setFreeDiscSpace(self):
        pass

    def getFreeDiscSpace(self):
        pass

    def setFreeMemory(self):
        pass

    def getFreeMemory(self):
        pass

    def setFreeCpu(self):
        pass

    def getFreeCpu(self):
        pass
    
    def setOStype(self, type):
        self.operatingSystemType = type

    def getOStype(self):
        return self.operatingSystemType

    def setOSversion(self, version):
        self.operatingSystemVersion = version

    def getOSversion(self):
        return self.operatingSystemVersion

    def setOSdist(self, dist):
        self.operatingSystemDistribution = dist

    def getOSdist(self):
        return self.operatingSystemDistribution

    def setVMs(self):
        vms = VM.objects.filter(serverID = name)
        for vm in vms:
            self.vms.add(vm)
    

        
        