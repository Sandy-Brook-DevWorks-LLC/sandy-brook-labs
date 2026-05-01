/**
 * KnowItOwl! — Dark Mode Toggle
 *
 * Wires up the #theme-toggle button (with #theme-toggle-dark-icon /
 * #theme-toggle-light-icon children) and persists the choice in localStorage.
 * The dark-class is applied/removed inline in the page <head> to prevent FOUC;
 * this script only handles the click interaction.
 */
document.addEventListener('DOMContentLoaded', function () {
    var darkIcon = document.getElementById('theme-toggle-dark-icon');
    var lightIcon = document.getElementById('theme-toggle-light-icon');
    var btn = document.getElementById('theme-toggle');
    if (!btn || !darkIcon || !lightIcon) return;

    var prefersDark = localStorage.getItem('theme') === 'dark'
        || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);

    if (prefersDark) {
        lightIcon.classList.remove('hidden');
    } else {
        darkIcon.classList.remove('hidden');
    }

    btn.addEventListener('click', function () {
        darkIcon.classList.toggle('hidden');
        lightIcon.classList.toggle('hidden');

        var stored = localStorage.getItem('theme');
        var isDark = document.documentElement.classList.contains('dark');

        if (stored) {
            if (stored === 'light') {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }
        } else if (isDark) {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    });
});
