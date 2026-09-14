<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/stores/auth';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Header from '$lib/components/Header.svelte';

	let isLoaded = false;

	onMount(() => {
		const token = localStorage.getItem('grc_token');
		if (!token && !$page.url.pathname.startsWith('/login')) {
			goto('/login');
		}
		isLoaded = true;
	});
</script>

{#if $page.url.pathname.startsWith('/login')}
	<main class="h-full w-full bg-slate-900 flex items-center justify-center p-4">
		<slot />
	</main>
{:else}
	<div class="flex h-full w-full bg-slate-50 overflow-hidden">
		<Sidebar />
		<div class="flex-1 flex flex-col min-w-0 overflow-hidden">
			<Header />
			<main class="flex-1 overflow-y-auto p-6">
				<slot />
			</main>
		</div>
	</div>
{/if}
