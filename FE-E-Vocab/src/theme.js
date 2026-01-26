export function getSavedTheme() {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark' || saved === 'light') return saved;
  return 'light';
}

export function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}

export function setTheme(theme) {
  localStorage.setItem('theme', theme);
  applyTheme(theme);
}

export function toggleTheme() {
  const next = getSavedTheme() === 'dark' ? 'light' : 'dark';
  setTheme(next);
  return next;
}

