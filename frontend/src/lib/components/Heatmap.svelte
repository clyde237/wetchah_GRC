<script lang="ts">
	export let data: Array<{ impact: number; likelihood: number; count: number }> = [];

	function getCount(imp: number, lik: number) {
		const item = data.find(d => d.impact === imp && d.likelihood === lik);
		return item ? item.count : 0;
	}

	function getCellColor(imp: number, lik: number) {
		const score = imp * lik;
		if (score >= 15) return 'bg-rose-500 text-white hover:bg-rose-600';
		if (score >= 10) return 'bg-amber-500 text-white hover:bg-amber-600';
		if (score >= 5) return 'bg-yellow-400 text-slate-900 hover:bg-yellow-500';
		return 'bg-emerald-500 text-white hover:bg-emerald-600';
	}
</script>

<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-sm font-bold text-slate-800 flex items-center gap-2">
			<span>🎯</span> Matrice 5×5 — Cartographie des Risques Résiduels
		</h3>
		<span class="text-xs text-slate-600">Impact × Vraisemblance</span>
	</div>

	<div class="flex gap-3">
		<!-- Axe vertical : Impact -->
		<div class="flex flex-col justify-between items-end pr-2 text-[11px] font-bold text-slate-600 w-24">
			<span class="text-rose-700">5. Critique</span>
			<span class="text-rose-600">4. Majeur</span>
			<span class="text-amber-600">3. Modéré</span>
			<span class="text-yellow-700">2. Mineur</span>
			<span class="text-emerald-700">1. Négligeable</span>
		</div>

		<!-- Grille 5x5 -->
		<div class="flex-1">
			<div class="grid grid-rows-5 gap-1.5 h-64">
				{#each [5, 4, 3, 2, 1] as imp}
					<div class="grid grid-cols-5 gap-1.5">
						{#each [1, 2, 3, 4, 5] as lik}
							{@const count = getCount(imp, lik)}
							<div
								class="rounded-lg flex flex-col items-center justify-center font-bold text-xs transition-transform transform hover:scale-105 cursor-pointer shadow-xs {getCellColor(imp, lik)}"
								title="Impact {imp}, Vraisemblance {lik} (Score {imp*lik}) : {count} risque(s)"
							>
								{#if count > 0}
									<span class="text-base">{count}</span>
									<span class="text-[10px] opacity-80 font-normal">rsq</span>
								{:else}
									<span class="opacity-30 text-[10px]">-</span>
								{/if}
							</div>
						{/each}
					</div>
				{/each}
			</div>

			<!-- Axe horizontal : Vraisemblance -->
			<div class="grid grid-cols-5 gap-1.5 mt-2 text-center text-[11px] font-bold text-slate-600">
				<span>1. Très rare</span>
				<span>2. Rare</span>
				<span>3. Possible</span>
				<span>4. Probable</span>
				<span class="text-rose-700">5. Fréquent</span>
			</div>
			<div class="text-center text-xs font-semibold text-slate-600 mt-2">Vraisemblance (Fréquence) ➔</div>
		</div>
	</div>
</div>
