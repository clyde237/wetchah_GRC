<script lang="ts">
	import { onMount } from 'svelte';
	import { apiRequest } from '$lib/api';

	let missions: any[] = [];
	let loading = true;

	onMount(async () => {
		try {
			missions = await apiRequest('/audit/missions');
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-2xl font-black text-slate-900 tracking-tight">Reporting & Centre d'Exports (Module 8)</h1>
		<p class="text-xs text-slate-500 mt-1">Génération de rapports PDF officiels et tableurs Excel pour la Direction et le Comité d'Audit (REP-01 à REP-04).</p>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
		<div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
			<div>
				<div class="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-2xl mb-4">
					📊
				</div>
				<h2 class="text-base font-bold text-slate-900">Registre Global des Risques (Excel)</h2>
				<p class="text-xs text-slate-500 mt-1">Export complet de l'ensemble des fiches de risques, scores bruts et résiduels, processus impactés et stratégies de traitement.</p>
			</div>
			<div class="mt-6 pt-4 border-t">
				<a
					href="/api/v1/reports/risks/excel"
					class="w-full py-2.5 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold transition-all shadow-sm flex items-center justify-center gap-2"
				>
					<span>Télécharger le Fichier Excel (.xlsx)</span>
				</a>
			</div>
		</div>

		<div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
			<div>
				<div class="w-12 h-12 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center text-2xl mb-4">
					📄
				</div>
				<h2 class="text-base font-bold text-slate-900">Rapports de Missions d'Audit Interne (PDF)</h2>
				<p class="text-xs text-slate-500 mt-1">Rapports d'audit officiels générés via ReportLab avec en-tête, constats, sévérités, recommandations et suivi des plans d'action.</p>
				
				<div class="mt-4 space-y-2">
					{#each missions as m}
						<div class="p-2.5 rounded-lg border border-slate-100 bg-slate-50 flex items-center justify-between">
							<span class="text-xs font-bold text-slate-800">{m.reference} — {m.title}</span>
							<a
								href="/api/v1/reports/missions/{m.id}/pdf"
								class="px-2.5 py-1 rounded bg-slate-900 text-white text-[11px] font-bold hover:bg-slate-800 transition-colors"
							>
								PDF
							</a>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>
</div>
