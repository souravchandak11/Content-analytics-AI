/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#2d6a6d",
                secondary: "#c06c52",
                charcoal: "#121212",
                offwhite: "#fdfbf7",
            },
            fontFamily: {
                serif: ["Playfair Display", "serif"],
                sans: ["Inter", "sans-serif"],
                editorial: ["Crimson Pro", "serif"],
            },
        },
    },
    plugins: [],
}
