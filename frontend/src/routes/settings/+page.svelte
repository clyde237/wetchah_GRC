<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let users: any[] = [];
	let logs: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			const [u, l] = await Promise.all([
				apiRequest('/users/'),
				apiRequest('/users/logs')
			]);
			users = u;
			logs = l;
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Administration & Traçabilité (Module 9)</h1>
		<p class="text-xs text-slate-500 mt-1">Gestion des utilisateurs, matrice RBAC et Journal d'Activité immuable (ADM-01 à ADM-05).</p>
	</div>

	<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
		<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
			<h2 class="text-sm font-bold text-slate-800 mb-3">Utilisateurs & Rôles</h2>
			<div class="divide-y divide-slate-100">
				{#each users as u}
					<div class="py-3 flex items-center justify-between">
						<div>
							<div class="text-xs font-bold text-slate-900">{u.full_name}</div>
							<div class="text-[11px] text-slate-500">{u.email}</div>
						</div>
						<div class="text-right">
							<span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-teal-50 text-teal-700 border border-teal-200">{u.role}</span>
							<div class="text-[10px] text-slate-400 mt-0.5">{u.department || 'Non renseigné'}</div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
			<h2 class="text-sm font-bold text-slate-800 mb-3">Journal d'Activité (Audit Trail)</h2>
			<div class="space-y-2 max-h-96 overflow-y-auto pr-1 text-xs">
				{#each logs as log}
					<div class="p-2.5 rounded-lg border border-slate-100 bg-slate-50/60 flex items-start justify-between">
						<div>
							<span class="font-bold text-slate-800">{log.user_name || 'Système'}</span>
							<span class="font-mono text-[10px] font-bold px-1 rounded bg-slate-200 text-slate-700 ml-1">{log.action}</span>
							<div class="text-[11px] text-slate-600 mt-0.5">{log.details || log.resource_type}</div>
						</div>
						<span class="text-[10px] text-slate-400 font-mono shrink-0">{new Date(log.created_at).toLocaleTimeString('fr-FR')}</span>
					</div>
				{/each}
			</div>
		</div>
	</div>
</div>
