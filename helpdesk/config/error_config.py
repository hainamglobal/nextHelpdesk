from enum import Enum
from helpdesk.config.status_code import StatusCode

class ErrorConfig(Enum):
    CREATE_CHANNEL_NO_ID = (StatusCode.BAD_REQUEST, "CHANNEL-ERR-400", "Tạo Channel thành công nhưng không nhận được ID trả về")
    API_CALL_ERROR = (StatusCode.INTERNAL_SERVER_ERROR, "API-ERR-500", "Lỗi gọi API đến {url}: {error}")
    API_CALL_DETAIL = (StatusCode.INTERNAL_SERVER_ERROR, "API-ERR-501", "\nChi tiết: {detail}")
    CREATE_CHANNEL_LOG_TITLE = (StatusCode.INTERNAL_SERVER_ERROR, "CHANNEL-ERR-502", "Lỗi tạo Raven Channel API")
    CREATE_CHANNEL_THROW = (StatusCode.INTERNAL_SERVER_ERROR, "CHANNEL-ERR-503", "Đã có lỗi xảy ra khi tạo Channel trên site Develop. Vui lòng kiểm tra Error Log.")
    ADD_MEMBER_LOG_TITLE = (StatusCode.INTERNAL_SERVER_ERROR, "MEMBER-ERR-500", "Lỗi thêm User vào Raven Channel")
    ADD_MEMBER_THROW = (StatusCode.INTERNAL_SERVER_ERROR, "MEMBER-ERR-501", "Đã có lỗi xảy ra khi thêm thành viên vào Channel trên site Develop. Vui lòng kiểm tra Error Log.")

    # agent ko tồn tại
    AGENT_NOT_EXIST = (StatusCode.NOT_FOUND ,"AGENT-ERR-001" ,"Nhân viên không tôn tại" )

    def __init__(self, status, error_code, message):
        self.status = status
        self.error_code = error_code
        self.message = message
