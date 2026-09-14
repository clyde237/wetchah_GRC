<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let risks: any[] = [];
	let loading = true;
	let showModal = false;
	let newRisk = {
		code: `RSK-${new Date().getFullYear()}-00${Math.floor(Math.random() * 90 + 10)}`,
		title: '',
		description: '',
		category: 'operationnel',
		process_affected: '',
		gross_impact: 3,
		gross_likelihood: 3,
		residual_impact: 2,
		residual_likelihood: 2,
		treatment_strategy: 'reduire',
		status: 'identifie'
	};

	onMount(loadRisks);

	async function loadRisks() {
		loading = true;
		try {
			risks = await apiRequest('/risks/');
		} catch (e: any) {
			console.error(e);
		} finally {
			loading = false;
		}
	}

	async function handleCreate() {
		try {
			await apiRequest('/risks/', {
				method: 'POST',
				body: JSON.stringify(newRisk)
			});
			showModal = false;
			await loadRisks();
		} catch (e: any) {
			alert('Erreur: ' + e.message);
		}
	}
</script>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-black text-slate-900 tracking-tight">Registre des Risques (Module 1)</h1>
			<p class="text-xs text-slate-500 mt-1">Identification, évaluation brute & résiduelle et plans de traitement (RIS-01 à RIS-08).</p>
		</div>
		<div class="flex items-center gap-2">
			<a href="/api/v1/reports/risks/excel" class="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2">
				<span>📊</span>
				<span>Exporter Excel</span>
			</a>
			<button on:click={() => showModal = true} class="px-3.5 py-2 rounded-lg bg-teal-600 hover:bg-teal-700 text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2">
				<span>➕</span>
				<span>Nouveau Risque</span>
			</button>
		</div>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement du registre des risques…</div>
	{:else}
		<div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
			<table class="w-full text-left text-xs">
				<thead class="bg-slate-50 border-b border-slate-200 text-slate-600 uppercase font-bold tracking-wider">
					<tr>
						<th class="py-3.5 px-4">Code</th>
						<th class="py-3.5 px-4">Titre du Risque</th>
						<th class="py-3.5 px-4">Catégorie</th>
						<th class="py-3.5 px-4">Processus</th>
						<th class="py-3.5 px-4 text-center">Score Brut</th>
						<th class="py-3.5 px-4 text-center">Score Résiduel</th>
						<th class="py-3.5 px-4">Stratégie</th>
						<th class="py-3.5 px-4">Statut</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each risks as r}
						<tr class="hover:bg-slate-50/60 transition-colors">
							<td class="py-3 px-4 font-mono font-bold text-teal-700">{r.code}</td>
							<td class="py-3 px-4">
								<div class="font-bold text-slate-800">{r.title}</div>
								<div class="text-[11px] text-slate-500 truncate max-w-md">{r.description}</div>
							</td>
							<td class="py-3 px-4 capitalize font-medium text-slate-600">{r.category}</td>
							<td class="py-3 px-4 text-slate-600">{r.process_affected || '-'}</td>
							<td class="py-3 px-4 text-center">
								<span class="px-2 py-0.5 rounded font-bold bg-slate-100 text-slate-700">
									{r.gross_score} (I{r.gross_impact}×V{r.gross_likelihood})
								</span>
							</td>
							<td class="py-3 px-4 text-center">
								<span class="px-2.5 py-0.5 rounded-full font-black {r.residual_score >= 12 ? 'bg-rose-100 text-rose-700' : r.residual_score >= 8 ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'}">
									{r.residual_score} (I{r.residual_impact}×V{r.residual_likelihood})
								</span>
							</td>
							<td class="py-3 px-4 capitalize font-semibold text-slate-700">{r.treatment_strategy}</td>
							<td class="py-3 px-4">
								<span class="px-2 py-0.5 rounded text-[11px] font-bold uppercase bg-slate-100 text-slate-600">
									{r.status}
								</span>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}

	<!-- Modale Nouveau Risque -->
	{#if showModal}
		<div class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
			<div class="bg-white rounded-2xl p-6 w-full max-w-xl shadow-2xl border border-slate-200">
				<h2 class="text-lg font-black text-slate-900 mb-4">Créer une Fiche de Risque</h2>
				<form on:submit|preventDefault={handleCreate} class="space-y-4">
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="block text-xs font-bold text-slate-700 mb-1" for="risk-code">Code</label>
							<input id="risk-code" bind:value={newRisk.code} required class="w-full px-3 py-2 border rounded-lg text-xs" />
						</div>
						<div>
							<label class="block text-xs font-bold text-slate-700 mb-1" for="risk-category">Catégorie</label>
							<select id="risk-category" bind:value={newRisk.category} class="w-full px-3 py-2 border rounded-lg text-xs">
								<option value="operationnel">Opérationnel</option>
								<option value="financier">Financier</option>
								<option value="it_cyber">IT & Cybersécurité</option>
								<option value="juridique">Juridique & Conformité</option>
								<option value="strategique">Stratégique</option>
							</select>
						</div>
					</div>
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1" for="risk-title">Titre du Risque</label>
						<input id="risk-title" bind:value={newRisk.title} required class="w-full px-3 py-2 border rounded-lg text-xs" placeholder="Ex: Défaut de comptage physique de caisse..." />
					</div>
					<div>
						<label class="block text-xs font-bold text-slate-700 mb-1" for="risk-desc">Description</label>
						<textarea id="risk-desc" bind:value={newRisk.description} required rows="2" class="w-full px-3 py-2 border rounded-lg text-xs"></textarea>
					</div>
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="block text-xs font-bold text-slate-700 mb-1" for="risk-impact">Impact Résiduel (1 à 5)</label>
							<input id="risk-impact" type="number" min="1" max="5" bind:value={newRisk.residual_impact} class="w-full px-3 py-2 border rounded-lg text-xs" />
						</div>
						<div>
							<label class="block text-xs font-bold text-slate-700 mb-1" for="risk-likelihood">Vraisemblance Résiduelle (1 à 5)</label>
							<input id="risk-likelihood" type="number" min="1" max="5" bind:value={newRisk.residual_likelihood} class="w-full px-3 py-2 border rounded-lg text-xs" />
						</div>
					</div>
					<div class="flex justify-end gap-2 pt-3 border-t">
						<button type="button" on:click={() => showModal = false} class="px-4 py-2 border rounded-lg text-xs font-bold">Annuler</button>
						<button type="submit" class="px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg text-xs font-bold">Enregistrer le risque</button>
					</div>
				</form>
			</div>
		</div>
	{/if}
</div>
