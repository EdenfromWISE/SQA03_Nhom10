import { useEffect } from 'react';

/**
 * Hook để thay đổi title của trang
 * @param {string} title - Tiêu đề muốn hiển thị trên tab trình duyệt
 */
export const useDocumentTitle = (title) => {
  useEffect(() => {
    const previousTitle = document.title;
    document.title = title ? `${title} - EVocab` : 'E-Vocab';
    
    // Cleanup: khôi phục title cũ khi component unmount (tùy chọn)
    return () => {
      document.title = previousTitle;
    };
  }, [title]);
};

