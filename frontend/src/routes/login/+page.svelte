<script lang="ts">
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';

	let email = 'controller@wetchah.local';
	let password = 'controller1234';
	let error = '';
	let loading = false;

	async function handleLogin() {
		loading = true;
		error = '';
		try {
			const res = await fetch('/api/v1/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email, password })
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: 'Identifiants invalides' }));
				throw new Error(err.detail || 'Connexion échouée');
			}

			const data = await res.json();
			auth.login(data.access_token, data.user);
			goto('/');
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	}

	function fillCredentials(userEmail: string, userPass: string) {
		email = userEmail;
		password = userPass;
	}
</script>

<div class="w-full max-w-md bg-white rounded-2xl shadow-xl border border-slate-800/10 p-8">
	<div class="text-center mb-8">
		<div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-teal-500/10 text-teal-600 text-3xl mb-3 shadow-inner">
			🛡️
		</div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Wetchah_GRC</h1>
		<p class="text-xs text-slate-500 mt-1">Espace Contrôle de Gestion & Audit Interne</p>
	</div>

	{#if error}
		<div class="mb-5 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
			<span>⚠️</span>
			<span>{error}</span>
		</div>
	{/if}

	<form on:submit|preventDefault={handleLogin} class="space-y-4">
		<div>
			<label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5" for="email">Email professionnel</label>
			<input
				id="email"
				type="email"
				bind:value={email}
				required
				class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all shadow-xs"
				placeholder="controleur@etablissement.cm"
			/>
		</div>

		<div>
			<label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5" for="password">Mot de passe</label>
			<input
				id="password"
				type="password"
				bind:value={password}
				required
				class="w-full px-3.5 py-2.5 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-500 transition-all shadow-xs"
				placeholder="••••••••"
			/>
		</div>

		<button
			type="submit"
			disabled={loading}
			class="w-full py-3 px-4 rounded-lg bg-teal-600 hover:bg-teal-700 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
		>
			{#if loading}
				<span>Connexion en cours…</span>
			{:else}
				<span>Se connecter au portail GRC</span>
			{/if}
		</button>
	</form>

	<div class="mt-8 pt-6 border-t border-slate-100">
		<div class="text-[11px] font-semibold text-slate-600 text-center uppercase tracking-wider mb-3">
			Connexion rapide (Profils par défaut)
		</div>
		<div class="grid grid-cols-3 gap-2">
			<button
				type="button"
				on:click={() => fillCredentials('controller@wetchah.local', 'controller1234')}
				class="px-2 py-1.5 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-[11px] font-bold text-slate-700 transition-colors"
			>
				Contrôleur
			</button>
			<button
				type="button"
				on:click={() => fillCredentials('auditor@wetchah.local', 'auditor1234')}
				class="px-2 py-1.5 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-[11px] font-bold text-slate-700 transition-colors"
			>
				Auditeur
			</button>
			<button
				type="button"
				on:click={() => fillCredentials('admin@wetchah.local', 'admin1234')}
				class="px-2 py-1.5 rounded bg-slate-50 hover:bg-slate-100 border border-slate-200 text-[11px] font-bold text-slate-700 transition-colors"
			>
				Admin
			</button>
		</div>
	</div>
</div>
