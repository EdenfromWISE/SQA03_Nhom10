import React from 'react';
import styles from './EmptyState.module.css';

function EmptyState({ 
  message = 'Không có dữ liệu', 
  icon = null,
  action = null 
}) {
  return (
    <div className={styles.emptyState}>
      {icon && <div className={styles.icon}>{icon}</div>}
      <p className={styles.message}>{message}</p>
      {action && <div className={styles.action}>{action}</div>}
    </div>
  );
}

export default EmptyState;

