import { toast, ToastOptions } from 'react-toastify';

// Default toast configuration
const defaultOptions: ToastOptions = {
  position: 'top-right',
  autoClose: 5000,
  hideProgressBar: false,
  closeOnClick: true,
  pauseOnHover: true,
  draggable: true,
};

// Success toast
export const showSuccess = (message: string, options?: ToastOptions) => {
  return toast.success(message, {
    ...defaultOptions,
    ...options,
  });
};

// Error toast
export const showError = (message: string, options?: ToastOptions) => {
  return toast.error(message, {
    ...defaultOptions,
    ...options,
  });
};

// Info toast
export const showInfo = (message: string, options?: ToastOptions) => {
  return toast.info(message, {
    ...defaultOptions,
    ...options,
  });
};

// Warning toast
export const showWarning = (message: string, options?: ToastOptions) => {
  return toast.warning(message, {
    ...defaultOptions,
    ...options,
  });
};

// Handle API errors and show appropriate toast
export const handleApiError = (error: any, fallbackMessage = 'An error occurred. Please try again.') => {
  console.error('API Error:', error);
  
  let errorMessage = fallbackMessage;
  
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const responseData = error.response.data;
    
    if (responseData.detail) {
      errorMessage = responseData.detail;
    } else if (responseData.message) {
      errorMessage = responseData.message;
    } else if (typeof responseData === 'string') {
      errorMessage = responseData;
    }
  } else if (error.request) {
    // The request was made but no response was received
    errorMessage = 'No response received from server. Please check your connection.';
  } else if (error.message) {
    // Something happened in setting up the request that triggered an Error
    errorMessage = error.message;
  }
  
  showError(errorMessage);
  return errorMessage;
};

// Dismiss all toasts
export const dismissAllToasts = () => {
  toast.dismiss();
};

export default {
  showSuccess,
  showError,
  showInfo,
  showWarning,
  handleApiError,
  dismissAllToasts,
};
