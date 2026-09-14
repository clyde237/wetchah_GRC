<script lang="ts">
	import { auth } from '$lib/stores/auth';
</script>

<header class="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0">
	<div class="flex items-center gap-3">
		<div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-md text-xs font-semibold bg-teal-50 text-teal-700 border border-teal-200">
			<span class="w-2 h-2 rounded-full bg-teal-500 animate-pulse"></span>
			<span>Liaison PMS Active</span>
		</div>
		<div class="text-xs text-slate-600">
			Synchronisé avec <span class="font-semibold text-slate-700">wetchah_app</span>
		</div>
	</div>

	<div class="flex items-center gap-4">
		{#if $auth}
			<div class="flex items-center gap-3 pr-2 border-r border-slate-200">
				<div class="text-right">
					<div class="text-sm font-bold text-slate-800">{$auth.full_name}</div>
					<div class="text-xs text-slate-600 font-mono capitalize">{$auth.role.replace('_', ' ')}</div>
				</div>
				<div class="w-9 h-9 rounded-full bg-slate-900 text-teal-400 font-bold flex items-center justify-center text-sm shadow-sm">
					{$auth.full_name.charAt(0)}
				</div>
			</div>
			<button
				on:click={() => auth.logout()}
				class="px-3 py-1.5 rounded-md text-xs font-semibold text-rose-600 hover:bg-rose-50 border border-rose-200 transition-colors flex items-center gap-1.5"
			>
				<span>Déconnexion</span>
			</button>
		{/if}
	</div>
</header>
