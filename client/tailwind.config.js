/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}', 'node_modules/preline/dist/*.js'],
	theme: {
		extend: {
			colors: {
				'custom-dark': '#1e1e1e',
			  },
		}
	},
	plugins: [require('preline/plugin')]
};
