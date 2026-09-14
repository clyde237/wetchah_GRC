<script lang="ts">
	export let title: string;
	export let value: string | number;
	export let subtitle: string = '';
	export let icon: string = '📈';
	export let alert: boolean = false;
	export let accent: string = 'teal';
</script>

<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-start justify-between">
	<div>
		<div class="text-xs font-semibold text-slate-600 uppercase tracking-wider">{title}</div>
		<div class="text-2xl font-black mt-1 text-slate-900">{value}</div>
		{#if subtitle}
			<div class="text-xs text-slate-600 mt-1 flex items-center gap-1">
				{#if alert}
					<span class="text-rose-700 font-bold">⚠️</span>
				{/if}
				<span>{subtitle}</span>
			</div>
		{/if}
	</div>
	<div class="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center text-xl shrink-0">
		{icon}
	</div>
</div>
