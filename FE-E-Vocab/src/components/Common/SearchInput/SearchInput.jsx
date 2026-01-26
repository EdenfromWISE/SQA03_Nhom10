import React from 'react';
import styles from './SearchInput.module.css';

function SearchInput({ 
  value, 
  onChange, 
  placeholder = 'Tìm kiếm...', 
  className = '' 
}) {
  return (
    <div className={`${styles.searchWrap} ${className}`}>
      <input
        type="text"
        className={styles.searchInput}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

export default SearchInput;

