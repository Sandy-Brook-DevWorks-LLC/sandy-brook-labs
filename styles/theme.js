/**
 * Sandy Brook — Dark Mode Theme Toggle
 *
 * Usage: Load this script in <head> (no defer) so toggleTheme() is available
 * when the nav button renders. Dark mode INIT should be a tiny inline script
 * BEFORE this file to prevent flash of wrong theme:
 *
 *   <script>
 *       if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) document.documentElement.classList.add('dark')
 *   </script>
 *   <script src="styles/theme.js"></script>
 */

function toggleTheme() {
    if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark')
        localStorage.theme = 'light'
    } else {
        document.documentElement.classList.add('dark')
        localStorage.theme = 'dark'
    }
}
