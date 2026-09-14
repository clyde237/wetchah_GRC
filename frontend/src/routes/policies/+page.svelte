<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let policies: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			policies = await apiRequest('/policies/');
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Politiques & Documentation (Module 4)</h1>
		<p class="text-xs text-slate-500 mt-1">Référentiel documentaire interne, procédures, versionnement et accusés de lecture (POL-01 à POL-05).</p>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement du référentiel documentaire…</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			{#each policies as p}
				<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
					<div>
						<div class="flex items-center justify-between">
							<span class="font-mono font-bold text-xs text-teal-700">{p.code}</span>
							<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-700">v{p.current_version}</span>
						</div>
						<h3 class="text-base font-bold text-slate-900 mt-2">{p.title}</h3>
						<p class="text-xs text-slate-500 mt-1">{p.content || 'Aucun contenu textuel consigné.'}</p>
					</div>
					<div class="mt-4 pt-3 border-t flex items-center justify-between text-xs">
						<span class="capitalize text-slate-500 font-medium">Type : {p.document_type}</span>
						<span class="px-2 py-0.5 rounded uppercase font-bold text-[10px] {p.status === 'publie' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">{p.status}</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
