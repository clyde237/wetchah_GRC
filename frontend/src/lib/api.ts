const BASE_URL = '/api/v1';

export async function apiRequest(endpoint: string, options: RequestInit = {}) {
	const token = typeof localStorage !== 'undefined' ? localStorage.getItem('grc_token') : null;

	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(options.headers as Record<string, string>)
	};

	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	const response = await fetch(`${BASE_URL}${endpoint}`, {
		...options,
		headers
	});

	if (response.status === 401) {
		if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
			localStorage.removeItem('grc_token');
			localStorage.removeItem('grc_user');
			window.location.href = '/login';
		}
		throw new Error('Non authentifié');
	}

	if (!response.ok) {
		const errData = await response.json().catch(() => ({ detail: response.statusText }));
		throw new Error(errData.detail || 'Une erreur est survenue');
	}

	return response.json();
}
