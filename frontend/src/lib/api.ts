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

/**
 * Télécharge un fichier produit par l'API (PDF, Excel).
 *
 * Un simple <a href> ne peut pas convenir : le jeton vit dans localStorage,
 * une navigation du navigateur n'envoie aucun en-tête Authorization et
 * l'endpoint répond 401. On récupère donc le fichier par fetch authentifié,
 * puis on déclenche la sauvegarde depuis le blob obtenu.
 */
export async function apiDownload(endpoint: string, fallbackName: string) {
	const token = typeof localStorage !== 'undefined' ? localStorage.getItem('grc_token') : null;

	const response = await fetch(`${BASE_URL}${endpoint}`, {
		headers: token ? { Authorization: `Bearer ${token}` } : {}
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
		throw new Error(errData.detail || 'Le téléchargement a échoué.');
	}

	// Le nom de fichier vient du serveur quand il le fournit — il porte la
	// référence de la mission, qu'on ne veut pas réinventer côté client.
	const disposition = response.headers.get('Content-Disposition') || '';
	const match = disposition.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
	const filename = match ? decodeURIComponent(match[1].trim()) : fallbackName;

	const blob = await response.blob();
	const url = URL.createObjectURL(blob);
	const link = document.createElement('a');
	link.href = url;
	link.download = filename;
	document.body.appendChild(link);
	link.click();
	link.remove();
	URL.revokeObjectURL(url);
}
