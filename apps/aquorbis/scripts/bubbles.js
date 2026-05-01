/**
 * Aquorbis — Background Bubbles
 *
 * Generates floating bubble divs inside any element with class="bubbles".
 * Reads the optional `data-count` attribute (default 20) so legal pages can
 * use a lower density than the landing page.
 */
(function () {
    'use strict';

    function init() {
        var container = document.querySelector('.bubbles');
        if (!container) return;
        var count = parseInt(container.getAttribute('data-count'), 10) || 20;

        for (var i = 0; i < count; i++) {
            var b = document.createElement('div');
            b.className = 'bubble';
            var size = 8 + Math.random() * 30;
            b.style.width = size + 'px';
            b.style.height = size + 'px';
            b.style.left = (Math.random() * 100) + '%';
            b.style.animationDuration = (8 + Math.random() * 12) + 's';
            b.style.animationDelay = (Math.random() * 10) + 's';
            container.appendChild(b);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
