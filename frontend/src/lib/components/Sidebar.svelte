<script lang="ts">
	import { page } from '$app/stores';
	import { auth } from '$lib/stores/auth';

	const navItems = [
		{ label: 'Tableau de bord', href: '/', icon: '📊' },
		{ label: 'Gestion des Risques', href: '/risks', icon: '⚠️' },
		{ label: 'Conformité & Normes', href: '/compliance', icon: '📜' },
		{ label: 'Contrôles & Audit', href: '/audit', icon: '🛡️' },
		{ label: 'Politiques & Docs', href: '/policies', icon: '📁' },
		{ label: 'Gestion des Incidents', href: '/incidents', icon: '🚨' },
		{ label: 'Évaluations en ligne', href: '/evaluations', icon: '📝' },
		{ label: 'Gestion des Tiers', href: '/third-parties', icon: '🤝' },
		{ label: 'Rapports & Exports', href: '/reports', icon: '📄' },
		{ label: 'Administration & Logs', href: '/settings', icon: '⚙️' }
	];
</script>

<aside class="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 border-r border-slate-800">
	<div class="h-16 flex items-center px-6 border-b border-slate-800 bg-slate-950/40">
		<span class="text-xl font-black tracking-tight text-white flex items-center gap-2">
			<span class="text-teal-400">🛡️</span> Wetchah<span class="text-teal-400 font-normal">GRC</span>
		</span>
	</div>

	<div class="px-4 py-3 border-b border-slate-800/60 bg-slate-950/20">
		<div class="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Module</div>
		<div class="text-xs text-teal-300 font-medium truncate">Contrôle de Gestion & Audit</div>
	</div>

	<nav class="flex-1 overflow-y-auto px-3 py-4 space-y-1">
		{#each navItems as item}
			{@const active = $page.url.pathname === item.href || (item.href !== '/' && $page.url.pathname.startsWith(item.href))}
			<a
				href={item.href}
				class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors {active ? 'bg-teal-500/10 text-teal-400 border border-teal-500/20' : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'}"
			>
				<span class="text-base">{item.icon}</span>
				<span>{item.label}</span>
			</a>
		{/each}
	</nav>

	<div class="p-4 border-t border-slate-800 bg-slate-950/40">
		<div class="text-[11px] text-slate-400">Plateforme WeTchah GRC v1.0</div>
		<div class="text-[10px] text-slate-500">Conforme SYSCOHADA & ISO 27001</div>
	</div>
</aside>
