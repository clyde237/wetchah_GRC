<script lang="ts">
	/**
	 * Les campagnes n'étaient qu'affichées : ni les liens à diffuser, ni le
	 * dépouillement n'avaient d'interface, alors que c'est précisément ce qui
	 * sert au contrôleur. Les deux sont ici.
	 */
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let questionnaires: any[] = [];
	let campaigns: any[] = [];
	let loading = true;
	let erreur = '';

	// Panneau latéral : liens de diffusion ou dépouillement d'une campagne.
	let ouverte: any = null;
	let vue: 'liens' | 'reponses' = 'liens';
	let liens: any[] = [];
	let reponses: any[] = [];
	let detail: any = null;
	let chargementPanneau = false;
	let copie = '';

	onMount(async () => {
		try {
			[questionnaires, campaigns] = await Promise.all([
				apiRequest('/evaluations/questionnaires'),
				apiRequest('/evaluations/campaigns')
			]);
		} catch (e: any) {
			erreur = e.message || 'Chargement impossible.';
		} finally {
			loading = false;
		}
	});

	async function ouvrir(camp: any, cible: 'liens' | 'reponses') {
		ouverte = camp;
		vue = cible;
		detail = null;
		chargementPanneau = true;
		erreur = '';
		try {
			if (cible === 'liens') {
				liens = await apiRequest(`/evaluations/campaigns/${camp.id}/links`);
			} else {
				reponses = await apiRequest(`/evaluations/campaigns/${camp.id}/responses`);
			}
		} catch (e: any) {
			erreur = e.message || 'Chargement impossible.';
		} finally {
			chargementPanneau = false;
		}
	}

	async function voirDetail(r: any) {
		chargementPanneau = true;
		try {
			detail = await apiRequest(`/evaluations/campaigns/${ouverte.id}/responses/${r.id}`);
		} catch (e: any) {
			erreur = e.message || 'Chargement impossible.';
		} finally {
			chargementPanneau = false;
		}
	}

	function copier(chemin: string) {
		const url = `${window.location.origin}${chemin}`;
		navigator.clipboard?.writeText(url);
		copie = chemin;
		setTimeout(() => (copie = ''), 1500);
	}

	function fermer() {
		ouverte = null;
		detail = null;
	}
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Évaluations en Ligne (Module 6)</h1>
		<p class="text-xs text-slate-500 mt-1">
			Questionnaires d'auto-évaluation, audits fournisseurs et consolidation des réponses (EVAL-01 à EVAL-05).
		</p>
	</div>

	{#if erreur}
		<div class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-medium text-rose-800">{erreur}</div>
	{/if}

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement des évaluations…</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<div>
				<h2 class="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3">Modèles de questionnaires</h2>
				<div class="space-y-3">
					{#each questionnaires as q}
						<div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
							<div class="flex items-center justify-between gap-3">
								<span class="text-xs font-bold text-slate-900">{q.title}</span>
								<span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-teal-50 text-teal-700 border border-teal-200">
									{q.target_type}
								</span>
							</div>
							<p class="text-xs text-slate-500 mt-1">{q.description || '—'}</p>
							<div class="text-[11px] text-slate-400 mt-2">{q.questions ? q.questions.length : 0} question(s)</div>
						</div>
					{:else}
						<div class="bg-white p-6 rounded-xl border border-slate-200 text-center text-xs text-slate-500">
							Aucun questionnaire.
						</div>
					{/each}
				</div>
			</div>

			<div>
				<h2 class="text-sm font-bold text-slate-700 uppercase tracking-wider mb-3">Campagnes</h2>
				<div class="space-y-3">
					{#each campaigns as camp}
						<div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
							<div class="flex items-center justify-between gap-3">
								<span class="text-xs font-bold text-slate-900">{camp.title}</span>
								<span class="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-100 text-slate-700">{camp.status}</span>
							</div>
							<div class="text-xs text-slate-500 mt-1">
								Échéance : {new Date(camp.deadline).toLocaleDateString('fr-FR')}
							</div>
							<div class="mt-2 text-[11px] text-teal-700 font-medium">
								{camp.completed_responses} / {camp.total_responses} réponse(s) reçue(s)
							</div>
							<div class="mt-3 flex gap-2">
								<button
									on:click={() => ouvrir(camp, 'liens')}
									class="rounded-lg border border-slate-300 px-3 py-1.5 text-[11px] font-bold text-slate-700 hover:bg-slate-50 transition-colors"
								>
									Liens à diffuser
								</button>
								<button
									on:click={() => ouvrir(camp, 'reponses')}
									disabled={camp.completed_responses === 0}
									class="rounded-lg bg-teal-600 px-3 py-1.5 text-[11px] font-bold text-white hover:bg-teal-700 disabled:opacity-40 transition-colors"
								>
									Dépouiller
								</button>
							</div>
						</div>
					{:else}
						<div class="bg-white p-6 rounded-xl border border-slate-200 text-center text-xs text-slate-500">
							Aucune campagne lancée.
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>

{#if ouverte}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
		<div class="w-full max-w-3xl max-h-[85vh] overflow-y-auto rounded-2xl bg-white shadow-xl">
			<div class="sticky top-0 flex items-start justify-between gap-4 border-b border-slate-100 bg-white px-6 py-4">
				<div>
					<div class="text-[11px] font-bold uppercase tracking-wider text-teal-600">
						{vue === 'liens' ? 'Liens de diffusion' : 'Dépouillement'}
					</div>
					<h2 class="text-base font-black text-slate-900">{ouverte.title}</h2>
				</div>
				<button on:click={fermer} class="text-xs font-bold text-slate-400 hover:text-slate-700">Fermer</button>
			</div>

			<div class="px-6 py-5">
				{#if chargementPanneau}
					<div class="py-10 text-center text-sm text-slate-500">Chargement…</div>

				{:else if vue === 'liens'}
					<p class="mb-4 text-xs text-slate-500 leading-relaxed">
						Ce module n'envoie pas de courriel : transmettez ces liens par votre propre canal.
						Chacun n'ouvre que le formulaire de son destinataire.
					</p>
					<div class="space-y-2">
						{#each liens as l}
							<div class="flex items-center justify-between gap-3 rounded-lg border border-slate-200 px-3 py-2">
								<div class="min-w-0">
									<div class="text-xs font-semibold text-slate-800">{l.respondent_name}</div>
									<div class="truncate text-[11px] text-slate-400">{l.respondent_email}</div>
								</div>
								<div class="flex shrink-0 items-center gap-2">
									{#if l.is_completed}
										<span class="rounded bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">Répondu</span>
									{:else}
										<button
											on:click={() => copier(l.path)}
											class="rounded border border-slate-300 px-2.5 py-1 text-[10px] font-bold text-slate-700 hover:bg-slate-50"
										>
											{copie === l.path ? 'Copié !' : 'Copier le lien'}
										</button>
									{/if}
								</div>
							</div>
						{/each}
					</div>

				{:else if detail}
					<button on:click={() => (detail = null)} class="mb-4 text-[11px] font-bold text-teal-600 hover:text-teal-700">
						← Retour aux réponses
					</button>
					<div class="mb-4 flex items-center gap-5 rounded-xl bg-slate-50 px-4 py-3 text-xs">
						<div>
							<div class="text-slate-400">Répondant</div>
							<div class="font-bold text-slate-800">{detail.respondent_name}</div>
						</div>
						<div>
							<div class="text-slate-400">Score</div>
							<div class="font-black text-teal-700">{detail.score}/100</div>
						</div>
						<div>
							<div class="text-slate-400">Points d'attention</div>
							<div class="font-black {detail.triggered_count > 0 ? 'text-rose-600' : 'text-emerald-600'}">
								{detail.triggered_count}
							</div>
						</div>
					</div>
					<div class="space-y-2">
						{#each detail.answers as a}
							<div class="rounded-lg border px-3 py-2 {a.triggered ? 'border-rose-200 bg-rose-50' : 'border-slate-200'}">
								<div class="text-[10px] font-bold uppercase tracking-wide text-slate-400">{a.section}</div>
								<div class="mt-0.5 text-xs font-semibold text-slate-800">{a.question_text}</div>
								<div class="mt-1 flex items-center gap-3 text-[11px]">
									<span class="text-slate-600">Réponse : <strong>{a.value ?? '—'}</strong></span>
									{#if a.scored_value !== null}
										<span class="text-slate-400">{a.scored_value}/100</span>
									{/if}
									{#if a.triggered}
										<span class="font-bold text-rose-700">⚠ à examiner</span>
									{/if}
								</div>
							</div>
						{/each}
					</div>

				{:else}
					<div class="space-y-2">
						{#each reponses as r}
							<button
								on:click={() => voirDetail(r)}
								disabled={!r.is_completed}
								class="flex w-full items-center justify-between gap-3 rounded-lg border border-slate-200 px-3 py-2 text-left hover:bg-slate-50 disabled:opacity-50 disabled:hover:bg-white"
							>
								<div class="min-w-0">
									<div class="text-xs font-semibold text-slate-800">{r.respondent_name}</div>
									<div class="truncate text-[11px] text-slate-400">{r.respondent_email}</div>
								</div>
								<div class="flex shrink-0 items-center gap-4 text-[11px]">
									{#if r.is_completed}
										{#if r.is_late}
											<span class="rounded bg-amber-50 px-2 py-0.5 font-bold text-amber-700">Tardive</span>
										{/if}
										{#if r.triggered_count > 0}
											<span class="font-bold text-rose-600">{r.triggered_count} point(s)</span>
										{/if}
										<span class="font-black text-teal-700">{r.score}/100</span>
									{:else}
										<span class="text-slate-400">En attente</span>
									{/if}
								</div>
							</button>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>
{/if}
