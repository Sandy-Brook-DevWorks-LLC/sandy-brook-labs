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

/**
 * Mobile Menu — Bottom Sheet Toggle
 *
 * Requires an element with id="mobile-menu" in the page.
 * See STYLE_GUIDE.md for the markup template.
 */
function toggleMenu() {
    var menu = document.getElementById('mobile-menu')
    if (!menu) return
    if (menu.classList.contains('open')) {
        menu.classList.remove('open')
        document.body.style.overflow = ''
    } else {
        menu.classList.add('open')
        document.body.style.overflow = 'hidden'
    }
}

function closeMenu() {
    var menu = document.getElementById('mobile-menu')
    if (menu) {
        menu.classList.remove('open')
        document.body.style.overflow = ''
    }
}
