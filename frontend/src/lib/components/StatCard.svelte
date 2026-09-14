<script lang="ts">
	export let title: string;
	export let value: string | number;
	export let subtitle: string = '';
	export let icon: any = null;
	export let alert: boolean = false;
	export let accent: string = 'teal';
</script>

<div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-start justify-between">
	<div>
		<div class="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</div>
		<div class="text-2xl font-black mt-1 text-slate-900">{value}</div>
		{#if subtitle}
			<div class="text-xs text-slate-500 mt-1 flex items-center gap-1">
				{#if alert}
					<span class="text-rose-600 font-bold">⚠️</span>
				{/if}
				<span>{subtitle}</span>
			</div>
		{/if}
	</div>
	<div class="w-10 h-10 rounded-lg {alert ? 'bg-rose-50 text-rose-600' : 'bg-slate-100 text-slate-700'} flex items-center justify-center shrink-0">
		{#if typeof icon === 'string'}
			<span class="text-xl">{icon}</span>
		{:else if icon}
			<svelte:component this={icon} class="w-5 h-5" />
		{/if}
	</div>
</div>
