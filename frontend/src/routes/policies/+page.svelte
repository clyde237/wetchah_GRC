<script lang="ts">
	/**
	 * Le cycle de vie documentaire — revue, approbation, publication,
	 * versions, accusés de lecture — n'existait que dans l'API : cette page
	 * se contentait de lister. Elle le pilote désormais.
	 */
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let policies: any[] = [];
	let loading = true;
	let erreur = '';

	let ouverte: any = null;          // fiche détaillée
	let travail = false;              // une action est en cours
	let nouvelleVersion = { version_number: '', change_summary: '', approve: false };

	const LIBELLES: Record<string, string> = {
		brouillon: 'Soumettre à revue',
		en_revue: 'Renvoyer en rédaction',
		approuve: 'Approuver',
		publie: 'Publier',
		archive: 'Archiver'
	};

	const TEINTES: Record<string, string> = {
		brouillon: 'bg-slate-100 text-slate-700',
		en_revue: 'bg-amber-100 text-amber-800',
		approuve: 'bg-blue-100 text-blue-800',
		publie: 'bg-emerald-100 text-emerald-800',
		archive: 'bg-slate-200 text-slate-500'
	};

	onMount(charger);

	async function charger() {
		loading = true;
		try {
			policies = await apiRequest('/policies/');
		} catch (e: any) {
			erreur = e.message || 'Chargement impossible.';
		} finally {
			loading = false;
		}
	}

	async function ouvrir(p: any) {
		erreur = '';
		nouvelleVersion = { version_number: '', change_summary: '', approve: false };
		try {
			ouverte = await apiRequest(`/policies/${p.id}`);
		} catch (e: any) {
			erreur = e.message || 'Ouverture impossible.';
		}
	}

	async function agir(action: () => Promise<any>) {
		travail = true;
		erreur = '';
		try {
			await action();
			ouverte = await apiRequest(`/policies/${ouverte.id}`);
			policies = await apiRequest('/policies/');
		} catch (e: any) {
			erreur = e.message || "L'action a échoué.";
		} finally {
			travail = false;
		}
	}

	const changerStatut = (statut: string) =>
		agir(() => apiRequest(`/policies/${ouverte.id}`, {
			method: 'PUT',
			body: JSON.stringify({ status: statut })
		}));

	const accuserReception = () =>
		agir(() => apiRequest(`/policies/${ouverte.id}/acknowledge`, { method: 'POST' }));

	const creerVersion = () =>
		agir(async () => {
			await apiRequest(`/policies/${ouverte.id}/versions`, {
				method: 'POST',
				body: JSON.stringify(nouvelleVersion)
			});
			nouvelleVersion = { version_number: '', change_summary: '', approve: false };
		});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Politiques &amp; Documentation (Module 4)</h1>
		<p class="text-xs text-slate-500 mt-1">
			Référentiel documentaire interne, procédures, versionnement et accusés de lecture (POL-01 à POL-05).
		</p>
	</div>

	{#if erreur && !ouverte}
		<div class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-xs font-medium text-rose-800">{erreur}</div>
	{/if}

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement du référentiel documentaire…</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
			{#each policies as p}
				<button
					on:click={() => ouvrir(p)}
					class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between text-left hover:border-teal-300 hover:shadow transition"
				>
					<div>
						<div class="flex items-center justify-between">
							<span class="font-mono font-bold text-xs text-teal-700">{p.code}</span>
							<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-slate-100 text-slate-700">v{p.current_version}</span>
						</div>
						<h3 class="text-base font-bold text-slate-900 mt-2">{p.title}</h3>
						<p class="text-xs text-slate-500 mt-1 line-clamp-2">{p.content || 'Aucun contenu textuel consigné.'}</p>
					</div>
					<div class="mt-4 pt-3 border-t flex items-center justify-between text-xs">
						<span class="text-slate-400 text-[11px]">
							{p.version_count} version(s) · {p.acknowledgment_count} lu(s)
						</span>
						<span class="px-2 py-0.5 rounded uppercase font-bold text-[10px] {TEINTES[p.status] ?? 'bg-slate-100 text-slate-700'}">
							{p.status}
						</span>
					</div>
				</button>
			{:else}
				<div class="md:col-span-2 bg-white p-8 rounded-xl border border-slate-200 text-center text-xs text-slate-500">
					Aucune politique enregistrée.
				</div>
			{/each}
		</div>
	{/if}
</div>

{#if ouverte}
	<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4">
		<div class="w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl bg-white shadow-xl">
			<div class="sticky top-0 flex items-start justify-between gap-4 border-b border-slate-100 bg-white px-6 py-4">
				<div>
					<div class="font-mono text-[11px] font-bold text-teal-600">{ouverte.code} · v{ouverte.current_version}</div>
					<h2 class="text-base font-black text-slate-900">{ouverte.title}</h2>
				</div>
				<button on:click={() => (ouverte = null)} class="text-xs font-bold text-slate-400 hover:text-slate-700">Fermer</button>
			</div>

			<div class="space-y-5 px-6 py-5">
				{#if erreur}
					<div class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-medium text-rose-800">{erreur}</div>
				{/if}

				<div class="flex flex-wrap items-center gap-2 text-xs">
					<span class="px-2 py-0.5 rounded uppercase font-bold text-[10px] {TEINTES[ouverte.status] ?? 'bg-slate-100'}">
						{ouverte.status}
					</span>
					{#if ouverte.next_review_date}
						<span class="text-slate-500">
							Revue prévue le {new Date(ouverte.next_review_date).toLocaleDateString('fr-FR')}
						</span>
					{/if}
				</div>

				{#if ouverte.content}
					<p class="rounded-lg bg-slate-50 px-3 py-2 text-xs leading-relaxed text-slate-700">{ouverte.content}</p>
				{/if}

				<!-- Étapes du cycle : seules celles que le serveur autorise -->
				<div>
					<div class="mb-2 text-[11px] font-bold uppercase tracking-wide text-slate-400">Cycle de vie</div>
					{#if ouverte.allowed_transitions.length}
						<div class="flex flex-wrap gap-2">
							{#each ouverte.allowed_transitions as etape}
								<button
									on:click={() => changerStatut(etape)}
									disabled={travail}
									class="rounded-lg border border-slate-300 px-3 py-1.5 text-[11px] font-bold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
								>
									{LIBELLES[etape] ?? etape}
								</button>
							{/each}
						</div>
					{:else}
						<p class="text-[11px] text-slate-400">Aucune étape ouverte depuis cet état.</p>
					{/if}
				</div>

				<!-- Accusé de lecture : réservé aux textes publiés -->
				<div class="rounded-lg border border-slate-200 px-3 py-2.5">
					<div class="flex items-center justify-between gap-3">
						<div>
							<div class="text-xs font-bold text-slate-800">Accusé de lecture</div>
							<div class="text-[11px] text-slate-500">{ouverte.acknowledgment_count} personne(s) ont accusé réception</div>
						</div>
						{#if ouverte.acknowledged_by_me}
							<span class="rounded bg-emerald-50 px-2.5 py-1 text-[11px] font-bold text-emerald-700">Vous avez accusé réception</span>
						{:else if ouverte.status === 'publie'}
							<button
								on:click={accuserReception}
								disabled={travail}
								class="rounded-lg bg-teal-600 px-3 py-1.5 text-[11px] font-bold text-white hover:bg-teal-700 disabled:opacity-50"
							>
								J'accuse réception
							</button>
						{:else}
							<span class="text-[11px] text-slate-400">Disponible une fois la politique publiée</span>
						{/if}
					</div>
				</div>

				<!-- Versions -->
				<div>
					<div class="mb-2 text-[11px] font-bold uppercase tracking-wide text-slate-400">
						Historique des versions ({ouverte.version_count})
					</div>
					<div class="space-y-1.5">
						{#each ouverte.versions as v}
							<div class="rounded-lg border border-slate-200 px-3 py-2 text-xs">
								<div class="flex items-center justify-between">
									<span class="font-mono font-bold text-slate-800">v{v.version_number}</span>
									<span class="text-[11px] {v.approved_at ? 'text-emerald-700 font-bold' : 'text-slate-400'}">
										{v.approved_at ? 'Approuvée' : 'En revue'}
									</span>
								</div>
								<p class="mt-0.5 text-[11px] text-slate-600">{v.change_summary}</p>
							</div>
						{:else}
							<p class="text-[11px] text-slate-400">Aucune version figée.</p>
						{/each}
					</div>

					<div class="mt-3 space-y-2 rounded-lg bg-slate-50 p-3">
						<div class="text-[11px] font-bold text-slate-600">Figer une nouvelle version</div>
						<p class="text-[10px] leading-relaxed text-slate-500">
							Une nouvelle version rouvre le cycle : le texte modifié n'est plus celui qui a été
							approuvé, et les accusés de lecture recueillis ne valent plus pour elle.
						</p>
						<div class="flex flex-wrap gap-2">
							<input
								bind:value={nouvelleVersion.version_number}
								placeholder="N° (ex. 2.0)"
								class="w-28 rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs focus:border-teal-500 focus:outline-none"
							/>
							<input
								bind:value={nouvelleVersion.change_summary}
								placeholder="Résumé des modifications"
								class="flex-1 min-w-[12rem] rounded-lg border border-slate-300 px-2.5 py-1.5 text-xs focus:border-teal-500 focus:outline-none"
							/>
						</div>
						<div class="flex items-center justify-between gap-3">
							<label class="inline-flex items-center gap-1.5 text-[11px] text-slate-600">
								<input type="checkbox" bind:checked={nouvelleVersion.approve} class="rounded border-slate-300" />
								Approuver dans la foulée
							</label>
							<button
								on:click={creerVersion}
								disabled={travail || !nouvelleVersion.version_number || !nouvelleVersion.change_summary}
								class="rounded-lg bg-slate-900 px-3 py-1.5 text-[11px] font-bold text-white hover:bg-slate-800 disabled:opacity-40"
							>
								Figer la version
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
