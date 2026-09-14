/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				grc: {
					50: '#f0fdfa',
					100: '#ccfbf1',
					200: '#99f6e4',
					500: '#14b8a6',
					600: '#0d9488',
					700: '#0f766e',
					800: '#115e59',
					900: '#134e4a',
					950: '#042f2e'
				}
			}
		}
	},
	plugins: []
};
