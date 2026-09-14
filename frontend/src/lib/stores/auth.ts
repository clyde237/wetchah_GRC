import { writable } from 'svelte/store';

export interface UserSession {
	id: number;
	email: string;
	full_name: string;
	role: string;
	department?: string;
	phone?: string;
}

function createAuthStore() {
	const initialUser = typeof localStorage !== 'undefined' && localStorage.getItem('grc_user')
		? JSON.parse(localStorage.getItem('grc_user') || 'null')
		: null;

	const { subscribe, set, update } = writable<UserSession | null>(initialUser);

	return {
		subscribe,
		login: (token: string, user: UserSession) => {
			if (typeof localStorage !== 'undefined') {
				localStorage.setItem('grc_token', token);
				localStorage.setItem('grc_user', JSON.stringify(user));
			}
			set(user);
		},
		logout: () => {
			if (typeof localStorage !== 'undefined') {
				localStorage.removeItem('grc_token');
				localStorage.removeItem('grc_user');
			}
			set(null);
			if (typeof window !== 'undefined') {
				window.location.href = '/login';
			}
		}
	};
}

export const auth = createAuthStore();
