<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let controls: any[] = [];
	let missions: any[] = [];
	let actionPlans: any[] = [];
	let loading = true;
	let activeTab = 'controls';

	onMount(async () => {
		try {
			const [c, m, p] = await Promise.all([
				apiRequest('/audit/controls'),
				apiRequest('/audit/missions'),
				apiRequest('/audit/action-plans')
			]);
			controls = c;
			missions = m;
			actionPlans = p;
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-black text-slate-900 tracking-tight">Contrôles Internes & Audit (Module 3)</h1>
			<p class="text-xs text-slate-500 mt-1">Catalogue des contrôles, tests, missions d'audit et plans d'action (AUD-01 à AUD-07).</p>
		</div>
		<div class="flex gap-1 bg-slate-200/70 p-1 rounded-xl">
			<button
				on:click={() => activeTab = 'controls'}
				class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all {activeTab === 'controls' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'}"
			>
				Contrôles Internes ({controls.length})
			</button>
			<button
				on:click={() => activeTab = 'missions'}
				class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all {activeTab === 'missions' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'}"
			>
				Missions d'Audit ({missions.length})
			</button>
			<button
				on:click={() => activeTab = 'plans'}
				class="px-3 py-1.5 rounded-lg text-xs font-bold transition-all {activeTab === 'plans' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'}"
			>
				Plans d'Action CAPA ({actionPlans.length})
			</button>
		</div>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement du module audit…</div>
	{:else if activeTab === 'controls'}
		<div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
			<table class="w-full text-left text-xs">
				<thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold tracking-wider">
					<tr>
						<th class="py-3 px-4">Code</th>
						<th class="py-3 px-4">Intitulé du Contrôle</th>
						<th class="py-3 px-4">Type</th>
						<th class="py-3 px-4">Fréquence</th>
						<th class="py-3 px-4">Méthode</th>
						<th class="py-3 px-4">Dernier Test</th>
						<th class="py-3 px-4">Résultat</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each controls as c}
						<tr class="hover:bg-slate-50/60">
							<td class="py-3 px-4 font-mono font-bold text-teal-700">{c.code}</td>
							<td class="py-3 px-4">
								<div class="font-bold text-slate-800">{c.title}</div>
								<div class="text-[11px] text-slate-500">{c.description}</div>
							</td>
							<td class="py-3 px-4 capitalize font-medium">{c.control_type}</td>
							<td class="py-3 px-4 capitalize">{c.frequency}</td>
							<td class="py-3 px-4 capitalize">{c.method}</td>
							<td class="py-3 px-4 text-slate-500">{c.last_test_date ? new Date(c.last_test_date).toLocaleDateString('fr-FR') : 'Jamais'}</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded font-bold {c.last_test_result === 'conforme' ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}">
									{c.last_test_result || 'N/A'}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{:else if activeTab === 'missions'}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			{#each missions as m}
				<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
					<div class="flex items-center justify-between">
						<span class="font-mono font-bold text-xs text-teal-700">{m.reference}</span>
						<span class="px-2 py-0.5 rounded text-[11px] font-bold uppercase bg-slate-100 text-slate-600">{m.status}</span>
					</div>
					<h3 class="text-base font-bold text-slate-900 mt-2">{m.title}</h3>
					<p class="text-xs text-slate-500 mt-1">{m.scope}</p>
					<div class="mt-4 pt-3 border-t flex items-center justify-between text-xs">
						<span class="text-slate-400">Du {new Date(m.start_date).toLocaleDateString('fr-FR')} au {new Date(m.end_date).toLocaleDateString('fr-FR')}</span>
						<a href="/api/v1/reports/missions/{m.id}/pdf" class="font-bold text-teal-600 hover:text-teal-700 flex items-center gap-1">
							<span>📄</span> Télécharger PDF
						</a>
					</div>
				</div>
			{/each}
		</div>
	{:else if activeTab === 'plans'}
		<div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
			<table class="w-full text-left text-xs">
				<thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold tracking-wider">
					<tr>
						<th class="py-3 px-4">Action Corrective</th>
						<th class="py-3 px-4">Échéance</th>
						<th class="py-3 px-4">Statut</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each actionPlans as p}
						<tr class="hover:bg-slate-50/60">
							<td class="py-3 px-4">
								<div class="font-bold text-slate-800">{p.title}</div>
								<div class="text-[11px] text-slate-500">{p.description}</div>
							</td>
							<td class="py-3 px-4 font-mono">{new Date(p.due_date).toLocaleDateString('fr-FR')}</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded font-bold uppercase bg-slate-100 text-slate-700">{p.status}</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
