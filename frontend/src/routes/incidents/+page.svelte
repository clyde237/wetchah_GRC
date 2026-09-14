<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let incidents: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			incidents = await apiRequest('/incidents/');
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Gestion des Incidents (Module 5)</h1>
		<p class="text-xs text-slate-500 mt-1">Déclaration, qualification, MTTR et capitalisation d'expérience REX (INC-01 à INC-05).</p>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement des incidents…</div>
	{:else}
		<div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
			<table class="w-full text-left text-xs">
				<thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold tracking-wider">
					<tr>
						<th class="py-3 px-4">Réf</th>
						<th class="py-3 px-4">Titre de l'Incident</th>
						<th class="py-3 px-4">Type</th>
						<th class="py-3 px-4">Sévérité</th>
						<th class="py-3 px-4">Date de survenance</th>
						<th class="py-3 px-4">Statut</th>
						<th class="py-3 px-4">REX / Leçons Apprises</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each incidents as inc}
						<tr class="hover:bg-slate-50/60">
							<td class="py-3 px-4 font-mono font-bold text-teal-700">{inc.reference}</td>
							<td class="py-3 px-4">
								<div class="font-bold text-slate-800">{inc.title}</div>
								<div class="text-[11px] text-slate-500">{inc.description}</div>
							</td>
							<td class="py-3 px-4 capitalize font-medium">{inc.incident_type}</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded font-bold {inc.severity === 'critique' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'}">
									{inc.severity}
								</span>
							</td>
							<td class="py-3 px-4 text-slate-500">{new Date(inc.occurred_at).toLocaleDateString('fr-FR')}</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded text-[11px] font-bold uppercase bg-slate-100 text-slate-700">{inc.status}</span>
							</td>
							<td class="py-3 px-4 text-[11px] text-slate-600 max-w-xs truncate">{inc.lessons_learned || '-'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
