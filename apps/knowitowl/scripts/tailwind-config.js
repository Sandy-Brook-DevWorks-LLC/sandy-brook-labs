/**
 * KnowItOwl! — Tailwind CDN configuration.
 *
 * Loaded immediately AFTER `<script src="https://cdn.tailwindcss.com"></script>`
 * so the global `tailwind` object exists. Defines the sage/cream palette and
 * the system-font stack used across all pages.
 */
tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                sage: {
                    DEFAULT: '#6B8E7E',
                    50: '#F4F7F6',
                    100: '#E9EFED',
                    200: '#D3E0DB',
                    300: '#BDD1C8',
                    400: '#A7C1B6',
                    500: '#91B2A4',
                    600: '#7B9D8E',
                    700: '#6B8E7E',
                    800: '#567265',
                    900: '#41564C',
                },
                cream: {
                    DEFAULT: '#FDFCF8',
                    dark: '#F5F2E8',
                },
            },
            fontFamily: {
                sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'Helvetica', 'Arial', 'sans-serif'],
            },
        },
    },
};
