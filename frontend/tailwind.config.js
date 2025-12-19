/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#09090b",
                surface: "#18181b",
                "surface-highlight": "#27272a",
                border: "#3f3f46",
                primary: "#3b82f6",
                "primary-hover": "#2563eb",
                success: "#22c55e",
                warning: "#f59e0b",
                danger: "#ef4444",
                text: "#f4f4f5",
                "text-muted": "#a1a1aa",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            }
        },
    },
    plugins: [],
}
