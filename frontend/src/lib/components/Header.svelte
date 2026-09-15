<script lang="ts">
	import { onMount } from 'svelte';
	import { auth } from '$lib/stores/auth';
	import { apiRequest } from '$lib/api';
	import { LogOut, Activity, AlertTriangle } from '@lucide/svelte';

	/** Établissement sur lequel ce module a été activé. */
	let etablissement = '';

	/**
	 * État réel de la liaison avec le PMS. L'en-tête annonçait « Liaison PMS
	 * Active » sans rien vérifier : la mention valait autant quand le PMS
	 * répondait que lorsqu'il était injoignable.
	 */
	let pms: { available: boolean; error?: string } | null = null;

	onMount(async () => {
		// /health ne demande pas d'authentification et porte l'identité du
		// conteneur : c'est la source du nom de l'établissement.
		try {
			const res = await fetch('/health');
			if (res.ok) etablissement = (await res.json()).tenant_name ?? '';
		} catch {
			/* l'en-tête se passe du nom plutôt que d'échouer */
		}

		try {
			pms = await apiRequest('/dashboard/pms');
		} catch {
			pms = null;
		}
	});
</script>

<header class="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0">
	<div class="flex items-center gap-3">
		{#if pms?.available}
			<div
				class="inline-flex items-center gap-2 px-2.5 py-1 rounded-md text-xs font-semibold bg-teal-50 text-teal-700 border border-teal-200"
			>
				<Activity class="w-3.5 h-3.5 text-teal-600 animate-pulse" />
				<span>Liaison PMS active</span>
			</div>
		{:else if pms}
			<div
				class="inline-flex items-center gap-2 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200"
				title={pms.error ?? ''}
			>
				<AlertTriangle class="w-3.5 h-3.5 text-amber-600" />
				<span>Liaison PMS interrompue</span>
			</div>
		{/if}

		{#if etablissement}
			<div class="text-xs text-slate-500">
				Établissement <span class="font-semibold text-slate-700">{etablissement}</span>
			</div>
		{/if}
	</div>

	<div class="flex items-center gap-4">
		{#if $auth}
			<div class="flex items-center gap-3 pr-2 border-r border-slate-200">
				<div class="text-right">
					<div class="text-sm font-bold text-slate-800">{$auth.full_name}</div>
					<div class="text-xs text-slate-500 font-mono capitalize">{$auth.role.replace('_', ' ')}</div>
				</div>
				<div
					class="w-9 h-9 rounded-full bg-slate-900 text-teal-400 font-bold flex items-center justify-center text-sm shadow-sm"
				>
					{$auth.full_name.charAt(0)}
				</div>
			</div>
			<button
				on:click={() => auth.logout()}
				class="px-3 py-1.5 rounded-md text-xs font-semibold text-rose-600 hover:bg-rose-50 border border-rose-200 transition-colors flex items-center gap-1.5"
			>
				<LogOut class="w-3.5 h-3.5" />
				<span>Déconnexion</span>
			</button>
		{/if}
	</div>
</header>
