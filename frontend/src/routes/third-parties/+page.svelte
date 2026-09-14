<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let thirdParties: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			thirdParties = await apiRequest('/third-parties/');
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Gestion des Tiers (Module 7)</h1>
		<p class="text-xs text-slate-500 mt-1">Référentiel des prestataires, évaluation des risques de la chaîne d'approvisionnement (TIERS-01 à TIERS-04).</p>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement des tiers…</div>
	{:else}
		<div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
			<table class="w-full text-left text-xs">
				<thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold tracking-wider">
					<tr>
						<th class="py-3 px-4">Nom du Tiers</th>
						<th class="py-3 px-4">Catégorie</th>
						<th class="py-3 px-4">Criticité</th>
						<th class="py-3 px-4">Contact</th>
						<th class="py-3 px-4">Contrat</th>
						<th class="py-3 px-4">Score Risque</th>
						<th class="py-3 px-4">Statut</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each thirdParties as tp}
						<tr class="hover:bg-slate-50/60">
							<td class="py-3 px-4 font-bold text-slate-900">{tp.name}</td>
							<td class="py-3 px-4 capitalize text-slate-600">{tp.category.replace('_', ' ')}</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded font-bold {tp.criticality === 'critique' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-700'}">
									{tp.criticality}
								</span>
							</td>
							<td class="py-3 px-4 text-slate-600">
								<div>{tp.contact_name || '-'}</div>
								<div class="text-[10px] text-slate-400">{tp.contact_phone || tp.contact_email || ''}</div>
							</td>
							<td class="py-3 px-4 font-mono text-[11px] text-slate-600">{tp.contract_reference || '-'}</td>
							<td class="py-3 px-4 font-bold text-slate-800">{tp.risk_score} / 5</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded uppercase font-bold text-[10px] bg-emerald-100 text-emerald-800">{tp.status}</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
