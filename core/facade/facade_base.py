from config.mapper import Mapper
from core.context.user_context import UserSession, get_user_session


class FacadeBase:

    def __init__(self, model_mapper: Mapper):
        self.model_mapper = model_mapper
        self.message_upload_password = ""
        self.message_reset_password = ""
        self.message_save = ""
        self.message_update = ""
        self.message_delete = ""
        self.path_base_front = ""
 
    @property
    def session(self) -> UserSession:
        return get_user_session()