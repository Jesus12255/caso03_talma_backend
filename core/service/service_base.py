from typing import Optional
from app.core.context.user_context import get_user_session, UserSession
from config.mapper import Mapper

class ServiceBase:

    def __init__(self):
        self.message_upload_password = ""
        self.message_reset_password = ""
        self.message_save = ""
        self.message_update = ""
        self.message_delete = ""
        self.path_base_front = ""

    @property
    def session(self) -> UserSession:
        return get_user_session()
    
    
