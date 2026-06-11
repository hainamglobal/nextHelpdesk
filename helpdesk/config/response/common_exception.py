class CommonException(Exception):
    def __init__(self, error_code):
        self.error_code = error_code
        super().__init__(error_code.message)
        # Kích hoạt luôn frappe.throw() để trả về định dạng chuẩn cho Frontend
        error_code.throw()
