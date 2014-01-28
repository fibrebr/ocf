from datetime import datetime, timedelta
from sqlalchemy.dialects.mysql import TINYINT, DOUBLE
from utils.base import db
import amsoil.core.log

logging=amsoil.core.log.getLogger('Expires')


'''@author: SergioVidiella'''

class Expires(db.Model):
    """Expiration time of the Virtual Machine (only GeniV3)."""
    __tablename__ = 'amsoil_vt_manager_expires'

    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    expires = db.Column(db.DateTime)
    do_save = True
    
    @staticmethod
    def constructor(expiration, save=True):
        self = Expires()
        try:
            logging.debug("********************************" + str(expiration))
            self.expires = expiration
            logging.debug("********************************" + str(self.expires))
            do_save = save
            if save:
                db.session.add(self)
                db.session.commit()
        except Exception as e:
            logging.debug("*********************************" + str(e))
            raise e
        return self
    
    def auto_save(self):
        if self.do_save:
            db.session.add(self)
            db.session.commit()
    
    '''Getters and Setters'''
    def set_expiration(self, expires):
        # XXX: Expiration validator?
        self.expires = expires
        self.auto_save()
    
    def get_expiration(self):
        return self.expires
    
    def get_vm(self):
        if self.expires_vm:
            return self.expires_vm[0].vm
        elif self.expires_allocated_vm:
            return self.expires_allocated_vm[0].allocated_vm
        else:
            return None

    def destroy(self):
        db.session.delete(self)
        db.session.commit()
