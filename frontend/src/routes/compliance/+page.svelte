<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let frameworks: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			frameworks = await apiRequest('/compliance/frameworks');
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Gestion de la Conformité (Module 2)</h1>
		<p class="text-xs text-slate-500 mt-1">Référentiels normatifs, exigences, écarts (gaps) et taux de conformité (CONF-01 à CONF-06).</p>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement des référentiels…</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			{#each frameworks as fw}
				<div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
					<div>
						<div class="flex items-center justify-between">
							<span class="px-2.5 py-1 rounded-md text-xs font-mono font-bold bg-teal-50 text-teal-700 border border-teal-200">
								{fw.code}
							</span>
							<span class="text-xs font-bold text-slate-400">v{fw.version}</span>
						</div>
						<h2 class="text-lg font-bold text-slate-900 mt-3">{fw.name}</h2>
						<p class="text-xs text-slate-500 mt-1">{fw.description || 'Référentiel standard'}</p>

						<div class="mt-6">
							<div class="flex justify-between text-xs font-bold mb-1.5">
								<span class="text-slate-700">Taux de conformité</span>
								<span class="text-teal-600">{fw.compliance_rate}%</span>
							</div>
							<div class="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden">
								<div class="h-full bg-teal-500 rounded-full" style="width: {fw.compliance_rate}%"></div>
							</div>
						</div>
					</div>

					<div class="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs">
						<span class="text-slate-500 font-medium">{fw.requirements ? fw.requirements.length : 0} exigence(s) suivie(s)</span>
						<button class="font-bold text-teal-600 hover:text-teal-700">Voir les exigences ➔</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
