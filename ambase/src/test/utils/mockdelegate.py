from src.abstract.classes.delegatebase import DelegateBase

class MockDelegate(DelegateBase):
    
    #TODO Mock Exceptions??
    
    def __init__(self, success_mode=True):
        self.success_mode = success_mode
     
    def get_version(self):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")
    
    def list_resources(self, geni_available=False):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")
    
    def describe(self, urns=dict(),credentials=dict(),options=dict()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")

    def reserve(self, slice_urn="", resources):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")
    
    def create(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")
    
    def delete(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error") 
    
    def perform_operational_action(self, urns=list(), action=None, geni_besteffort=True):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")
            
    def status(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")
        
    def renew(self, urns=list(), expiration_time=None):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")
        
    def shut_down(self, urns=list()):
        if self.success_mode:
            return True
        else:
            raise Exception("Mock Error")