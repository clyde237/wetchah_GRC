<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let questionnaires: any[] = [];
	let campaigns: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			const [q, c] = await Promise.all([
				apiRequest('/evaluations/questionnaires'),
				apiRequest('/evaluations/campaigns')
			]);
			questionnaires = q;
			campaigns = c;
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Évaluations en Ligne (Module 6)</h1>
		<p class="text-xs text-slate-500 mt-1">Questionnaires d'auto-évaluation, audits fournisseurs et consolidation des réponses (EVAL-01 à EVAL-05).</p>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement des évaluations…</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
			<div>
				<h2 class="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3">Modèles de Questionnaires</h2>
				<div class="space-y-3">
					{#each questionnaires as q}
						<div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
							<div class="flex items-center justify-between">
								<span class="text-xs font-bold text-slate-900">{q.title}</span>
								<span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-teal-50 text-teal-700 border border-teal-200">{q.target_type}</span>
							</div>
							<p class="text-xs text-slate-500 mt-1">{q.description || '-'}</p>
							<div class="text-[11px] text-slate-400 mt-2">{q.questions ? q.questions.length : 0} question(s)</div>
						</div>
					{/each}
				</div>
			</div>

			<div>
				<h2 class="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3">Campagnes d'Évaluation en Cours</h2>
				<div class="space-y-3">
					{#each campaigns as camp}
						<div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
							<div class="flex items-center justify-between">
								<span class="text-xs font-bold text-slate-900">{camp.title}</span>
								<span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-100 text-slate-700">{camp.status}</span>
							</div>
							<div class="text-xs text-slate-500 mt-1">Date limite : {new Date(camp.deadline).toLocaleDateString('fr-FR')}</div>
							<div class="mt-2 text-[11px] text-teal-700 font-medium">
								{camp.completed_responses} / {camp.total_responses} réponse(s) reçue(s)
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>
