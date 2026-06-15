import { useClipboard } from "@vueuse/core";
import { toast } from "frappe-ui";
import { ref } from "vue";

/**
 * Wrapper to create toasts, supplied with default options.
 * https://frappeui.com/components/toast.html
 * @param options - `Toast` options
 */
export function createToast(options?: Record<string, string>) {
  toast({
    position: "bottom-right",
    ...options,
  });
}

/**
 * Copy a string to clipboard, and create a toast
 * @param s - String to copy
 */
export async function copy(s: string) {
  const { copy: c } = useClipboard();
  c(s).then(() =>
    createToast({
      title: "Copied to clipboard",
      icon: "check",
      iconClasses: "text-green-600",
    })
  );
}

/**
 * Get assigned user from `_assign` string. The return value is a `string`,
 * not a `User` object.
 * @param s - `_assign` string (JSON)
 * @returns user id
 */
export function getAssign(s: string): string | undefined {
  const assignJson = JSON.parse(s);
  const arr = Array.isArray(assignJson) ? assignJson : [];
  return arr.slice(-1).pop();
}

/**
 * Map error codes from backend to localized user-friendly messages
 * @param errorCode - Error code string (e.g. AGENT-ERR-002)
 * @returns Object with title and message
 */
export function getErrorMessage(errorCode: string): { title: string; message: string } | null {
  const errorMap: Record<string, { title: string; message: string }> = {
    "SYS-ERR-403": {
      title: "Lỗi phân quyền",
      message: "Bạn không có quyền thực hiện thao tác này.",
    },
    "AGENT-ERR-001": {
      title: "Lỗi tạo Agent",
      message: "Nhân viên không tồn tại.",
    },
    "AGENT-ERR-002": {
      title: "Lỗi tạo Agent",
      message: "Đã xảy ra lỗi trong quá trình tạo Agent trên server. Dữ liệu đã được rollback.",
    },
    "AGENT-ERR-003": {
      title: "Lỗi xóa Agent",
      message: "Phải có ít nhất một nhân viên để có thể nhận được các phiếu đã được giao.",
    },
    "CHANNEL-ERR-400": {
      title: "Lỗi Channel",
      message: "Tạo Channel thành công nhưng không nhận được ID trả về.",
    },
    "CHANNEL-ERR-502": {
      title: "Lỗi Channel",
      message: "Lỗi tạo Raven Channel API.",
    },
    "CHANNEL-ERR-503": {
      title: "Lỗi Channel",
      message: "Đã có lỗi xảy ra khi tạo Channel trên site Develop. Vui lòng kiểm tra Error Log.",
    },
    "MEMBER-ERR-500": {
      title: "Lỗi Thành viên",
      message: "Lỗi thêm User vào Raven Channel.",
    },
    "MEMBER-ERR-501": {
      title: "Lỗi Thành viên",
      message: "Đã có lỗi xảy ra khi thêm thành viên vào Channel trên site Develop. Vui lòng kiểm tra Error Log.",
    },
  };

  return errorMap[errorCode] || null;
}

export function parseBackendError(err: any): { title: string; message: string } {
  let title = "Lỗi hệ thống";
  let message = "Đã xảy ra lỗi không xác định.";

  let responseData = err?.response?.data || err;
  let errorCode = responseData?.error_code || err?.error_code;
  const errorMessage = responseData?.error_message || err?.error_message;
  const statusCode = err?.response?.status || responseData?.http_status_code || err?.http_status_code || "";

  // Nếu frappe-ui nuốt mất error_code ở root, ta mò trong mảng messages xem backend có nhét [MÃ-LỖI] vào không
  if (!errorCode && err.messages && Array.isArray(err.messages)) {
    for (const msg of err.messages) {
      const match = msg.match(/^\[([A-Z]+-ERR-\d+)\]/);
      if (match) {
        errorCode = match[1];
        break;
      }
    }
  }

  // 1. Dựa vào errorCode từ backend để lấy map chuẩn
  if (errorCode) {
    const mapped = getErrorMessage(errorCode);
    if (mapped) {
      title = mapped.title;
      message = mapped.message;
    } else {
      title = `Lỗi ${errorCode}`;
      message = errorMessage || (err.messages ? err.messages.join(", ") : message);
    }
  } 
  // 2. Fallback nếu backend không trả error_code cụ thể mà chỉ ném list text
  else if (err.messages && Array.isArray(err.messages)) {
    for (const msg of err.messages) {
      const mappedError = getErrorMessage(msg);
      if (mappedError) {
        title = mappedError.title;
        message = mappedError.message;
        break;
      }
    }
    if (title === "Lỗi hệ thống" && err.messages.length > 0) {
      message = err.messages.join(", ");
    }
  } 
  // 3. Các trường hợp lỗi network, lỗi python ngẫu nhiên
  else if (errorMessage) {
    message = errorMessage;
  } else if (err.message) {
    message = err.message;
  } else if (err.exc) {
    message = "Lỗi xử lý API từ máy chủ.";
  }

  // Luôn gắn status code nếu có
  if (statusCode && !message.includes(`[Lỗi ${statusCode}]`)) {
    message = `[Lỗi ${statusCode}] ${message}`;
  }

  return { title, message };
}

export const globalErrorState = ref({
  show: false,
  title: "",
  message: "",
});

export function showGlobalError(err: any) {
  const { title, message } = parseBackendError(err);
  globalErrorState.value = {
    show: true,
    title,
    message,
  };
}
