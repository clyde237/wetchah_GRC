<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';
	import StatCard from '$lib/components/StatCard.svelte';
	import Heatmap from '$lib/components/Heatmap.svelte';
	import {
		AlertTriangle,
		ShieldCheck,
		ShieldAlert,
		Siren,
		Clock,
		FileDown,
		Zap
	} from '@lucide/svelte';

	let loading = true;
	let data: any = null;
	let error = '';

	onMount(async () => {
		try {
			data = await apiRequest('/dashboard/');
		} catch (e: any) {
			error = e.message;
		} finally {
			loading = false;
		}
	});

	function formatCurrency(val: number) {
		return new Intl.NumberFormat('fr-FR').format(val) + ' FCFA';
	}
</script>

<div class="space-y-6">
	<!-- Titre & Bandeau haut -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-black text-slate-900 tracking-tight">Tableau de Bord de Contrôle & Gouvernance</h1>
			<p class="text-xs text-slate-500 mt-1">Surveillance consolidée des risques, conformité, audits et flux opérationnels PMS.</p>
		</div>
		<div class="flex items-center gap-2">
			<a href="/reports" class="px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-all shadow-sm flex items-center gap-2">
				<FileDown class="w-4 h-4" />
				<span>Générer un Rapport d'Audit (PDF)</span>
			</a>
		</div>
	</div>

	{#if loading}
		<div class="p-12 text-center text-slate-500 text-sm">Chargement des données consolidées…</div>
	{:else if error}
		<div class="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-sm">
			Erreur : {error}
		</div>
	{:else if data}
		<!-- Métriques Principales GRC -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
			<StatCard
				title="Risques Critiques"
				value={data.critical_risks}
				subtitle={data.critical_risks > 0 ? 'Action prioritaire requise' : 'Aucun risque critique'}
				icon={AlertTriangle}
				alert={data.critical_risks > 0}
			/>
			<StatCard
				title="Taux de Conformité"
				value="{data.overall_compliance_rate}%"
				subtitle="Standards ISO & OHADA"
				icon={ShieldCheck}
			/>
			<StatCard
				title="Contrôles Échoués"
				value={data.failed_controls}
				subtitle="Sur {data.active_controls} contrôles actifs"
				icon={ShieldAlert}
				alert={data.failed_controls > 0}
			/>
			<StatCard
				title="Incidents en Cours"
				value={data.open_incidents}
				subtitle="En cours de qualification"
				icon={Siren}
				alert={data.open_incidents > 0}
			/>
			<StatCard
				title="Plans d'Action en Retard"
				value={data.delayed_action_plans}
				subtitle="Sur {data.active_action_plans} actions actives"
				icon={Clock}
				alert={data.delayed_action_plans > 0}
			/>
		</div>

		<!-- Cartouche d'intégration temps réel avec wetchah_app -->
		{#if data.wetchah_financial_summary}
			{@const fin = data.wetchah_financial_summary}
			<div class="bg-gradient-to-r from-slate-900 to-slate-800 text-white p-5 rounded-2xl shadow-md border border-slate-700">
				<div class="flex items-center justify-between mb-3 border-b border-slate-700/60 pb-3">
					<div class="flex items-center gap-2">
						<span class="text-teal-400 text-lg">⚡</span>
						<span class="text-xs font-black uppercase tracking-wider text-teal-400">Flux Opérationnel PMS Consommé (wetchah_app)</span>
					</div>
					<span class="text-[11px] text-slate-400 font-mono">Données via API PMS sécurisée</span>
				</div>
				<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div>
						<div class="text-[11px] text-slate-400 font-medium">Recettes du Jour</div>
						<div class="text-xl font-black text-white mt-0.5">{formatCurrency(fin.today_revenue || 0)}</div>
					</div>
					<div>
						<div class="text-[11px] text-slate-400 font-medium">Taux d'Occupation Hôtel</div>
						<div class="text-xl font-black text-teal-300 mt-0.5">{fin.occupancy_rate || 0}%</div>
					</div>
					<div>
						<div class="text-[11px] text-slate-400 font-medium">Sessions Caisse Ouvertes</div>
						<div class="text-xl font-black text-white mt-0.5">{fin.open_cash_sessions || 0} caisse(s)</div>
					</div>
					<div>
						<div class="text-[11px] text-slate-400 font-medium">Écarts Caisse Détectés</div>
						<div class="text-xl font-black {fin.cash_discrepancies_count > 0 ? 'text-rose-400' : 'text-emerald-400'} mt-0.5">
							{fin.cash_discrepancies_count || 0} anomalie(s)
						</div>
					</div>
				</div>
			</div>
		{/if}

		<!-- Matrice 5x5 et Top Risques -->
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<!-- Heatmap -->
			<Heatmap data={data.heatmap} />

			<!-- Top Risques -->
			<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
						<span>🔥</span> Top 5 Risques Prioritaires
					</h3>
					<a href="/risks" class="text-xs font-bold text-teal-600 hover:text-teal-700">Voir tout ➔</a>
				</div>

				<div class="space-y-3 flex-1">
					{#each data.top_risks as r}
						<div class="p-3 rounded-lg border border-slate-100 bg-slate-50/60 hover:bg-slate-50 transition-colors flex items-center justify-between">
							<div>
								<div class="flex items-center gap-2">
									<span class="text-xs font-mono font-bold text-slate-500">{r.code}</span>
									<span class="text-xs font-bold text-slate-800">{r.title}</span>
								</div>
								<div class="text-[11px] text-slate-500 mt-0.5 capitalize">
									Catégorie : {r.category} | Statut : <span class="font-medium text-slate-700">{r.status}</span>
								</div>
							</div>
							<div class="text-right">
								<div class="inline-flex items-center px-2 py-0.5 rounded text-xs font-black {r.residual_score >= 12 ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'}">
									Score : {r.residual_score}
								</div>
								<div class="text-[10px] text-slate-600">Brut : {r.gross_score}</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>
