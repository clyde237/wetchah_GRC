<script lang="ts">
	/**
	 * Formulaire d'évaluation destiné à un répondant sans compte GRC
	 * (chef de service, fournisseur…). L'accès tient au seul jeton présent
	 * dans l'URL : on n'utilise donc ni le store d'authentification, ni le
	 * client apiRequest, qui redirigerait vers /login au premier 401.
	 */
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let form: any = null;
	let loading = true;
	let loadError = '';
	let submitting = false;
	let submitError = '';
	let submitted: any = null;

	const answers: Record<number, string> = {};

	$: token = $page.params.token;

	onMount(async () => {
		try {
			const res = await fetch(`/api/v1/evaluations/respond/${token}`);
			if (!res.ok) {
				const data = await res.json().catch(() => ({}));
				throw new Error(data.detail || "Ce lien d'évaluation n'est pas valide.");
			}
			form = await res.json();
		} catch (e: any) {
			loadError = e.message;
		} finally {
			loading = false;
		}
	});

	function unanswered(): number {
		if (!form) return 0;
		return form.questions.filter((q: any) => !(answers[q.id] ?? '').trim()).length;
	}

	async function submit() {
		submitting = true;
		submitError = '';
		try {
			const payload = {
				answers: form.questions
					.filter((q: any) => (answers[q.id] ?? '').trim())
					.map((q: any) => ({ question_id: q.id, value: answers[q.id] }))
			};

			const res = await fetch(`/api/v1/evaluations/respond/${token}`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			if (!res.ok) {
				const data = await res.json().catch(() => ({}));
				throw new Error(data.detail || "L'envoi a échoué.");
			}
			submitted = await res.json();
		} catch (e: any) {
			submitError = e.message;
		} finally {
			submitting = false;
		}
	}

	const SCALE = [
		{ value: '1', label: '1 — Jamais' },
		{ value: '2', label: '2 — Rarement' },
		{ value: '3', label: '3 — Parfois' },
		{ value: '4', label: '4 — Souvent' },
		{ value: '5', label: '5 — Toujours' }
	];
</script>

<svelte:head>
	<title>Évaluation — Wetchah GRC</title>
</svelte:head>

<div class="min-h-screen w-full bg-slate-100 py-10 px-4">
	<div class="mx-auto max-w-2xl">
		{#if loading}
			<div class="rounded-2xl bg-white p-12 text-center text-sm text-slate-500 shadow-sm">
				Chargement du questionnaire…
			</div>

		{:else if loadError}
			<div class="rounded-2xl border border-rose-200 bg-white p-10 text-center shadow-sm">
				<div class="text-3xl">🔒</div>
				<h1 class="mt-3 text-lg font-black text-slate-900">Lien inaccessible</h1>
				<p class="mt-2 text-sm text-slate-600">{loadError}</p>
				<p class="mt-4 text-xs text-slate-400">
					Rapprochez-vous du contrôle de gestion pour obtenir un nouveau lien.
				</p>
			</div>

		{:else if submitted}
			<div class="rounded-2xl border border-emerald-200 bg-white p-10 text-center shadow-sm">
				<div class="text-3xl">✅</div>
				<h1 class="mt-3 text-lg font-black text-slate-900">Évaluation enregistrée</h1>
				<p class="mt-2 text-sm text-slate-600">{submitted.message}</p>
				<div class="mt-5 inline-flex items-center gap-4 rounded-xl bg-slate-50 px-5 py-3 text-xs">
					<div>
						<div class="text-slate-400 font-medium">Réponses transmises</div>
						<div class="mt-0.5 text-base font-black text-slate-800">{submitted.answered}</div>
					</div>
					<div class="h-8 w-px bg-slate-200"></div>
					<div>
						<div class="text-slate-400 font-medium">Score de conformité</div>
						<div class="mt-0.5 text-base font-black text-teal-700">{submitted.score}/100</div>
					</div>
				</div>
				{#if submitted.is_late}
					<p class="mt-4 text-xs font-semibold text-amber-700">
						Réponse transmise après l'échéance — elle est enregistrée et signalée comme telle.
					</p>
				{/if}
				<p class="mt-5 text-xs text-slate-400">Vous pouvez fermer cette page.</p>
			</div>

		{:else if form.is_completed}
			<div class="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
				<div class="text-3xl">📋</div>
				<h1 class="mt-3 text-lg font-black text-slate-900">Évaluation déjà transmise</h1>
				<p class="mt-2 text-sm text-slate-600">
					Vos réponses à « {form.campaign_title} » ont déjà été enregistrées.
					Elles ne peuvent plus être modifiées.
				</p>
			</div>

		{:else if form.is_closed}
			<div class="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
				<div class="text-3xl">🔐</div>
				<h1 class="mt-3 text-lg font-black text-slate-900">Campagne clôturée</h1>
				<p class="mt-2 text-sm text-slate-600">
					La campagne « {form.campaign_title} » est close et n'accepte plus de réponse.
				</p>
			</div>

		{:else}
			<div class="overflow-hidden rounded-2xl bg-white shadow-sm">
				<div class="bg-slate-900 px-7 py-6 text-white">
					<div class="text-[11px] font-bold uppercase tracking-wider text-teal-400">
						Évaluation de contrôle interne
					</div>
					<h1 class="mt-1.5 text-xl font-black">{form.questionnaire_title}</h1>
					<p class="mt-1 text-xs text-slate-300">{form.campaign_title}</p>
					{#if form.questionnaire_description}
						<p class="mt-3 border-t border-slate-700/60 pt-3 text-xs leading-relaxed text-slate-300">
							{form.questionnaire_description}
						</p>
					{/if}
					<div class="mt-4 flex flex-wrap items-center gap-x-5 gap-y-1 text-[11px] text-slate-400">
						<span>Répondant : <strong class="text-slate-200">{form.respondent_name}</strong></span>
						<span>
							Échéance : <strong class="text-slate-200">
								{new Date(form.deadline).toLocaleDateString('fr-FR')}
							</strong>
						</span>
					</div>
				</div>

				{#if form.is_past_deadline}
					<div class="border-b border-amber-200 bg-amber-50 px-7 py-3 text-xs font-medium text-amber-800">
						L'échéance est dépassée. Votre réponse reste acceptée, mais elle sera signalée comme tardive.
					</div>
				{/if}

				<div class="space-y-6 px-7 py-7">
					{#each form.questions as q, i}
						<div>
							<div class="flex gap-2.5">
								<span class="mt-0.5 shrink-0 text-[11px] font-black text-slate-300">
									{String(i + 1).padStart(2, '0')}
								</span>
								<div class="flex-1">
									<div class="text-[10px] font-bold uppercase tracking-wide text-teal-600">
										{q.section}
									</div>
									<label for="q-{q.id}" class="mt-0.5 block text-sm font-semibold text-slate-800">
										{q.question_text}
									</label>

									<div class="mt-2.5">
										{#if q.question_type === 'yes_no'}
											<div class="flex gap-2">
												{#each [['oui', 'Oui'], ['non', 'Non']] as [value, label]}
													<button
														type="button"
														on:click={() => (answers[q.id] = value)}
														class="rounded-lg border px-4 py-1.5 text-xs font-bold transition-colors
															{answers[q.id] === value
																? 'border-teal-600 bg-teal-600 text-white'
																: 'border-slate-300 bg-white text-slate-600 hover:border-slate-400'}"
													>
														{label}
													</button>
												{/each}
											</div>
										{:else if q.question_type === 'scale_1_5'}
											<div class="flex flex-wrap gap-2">
												{#each SCALE as opt}
													<button
														type="button"
														on:click={() => (answers[q.id] = opt.value)}
														class="rounded-lg border px-3 py-1.5 text-[11px] font-bold transition-colors
															{answers[q.id] === opt.value
																? 'border-teal-600 bg-teal-600 text-white'
																: 'border-slate-300 bg-white text-slate-600 hover:border-slate-400'}"
													>
														{opt.label}
													</button>
												{/each}
											</div>
										{:else}
											<textarea
												id="q-{q.id}"
												bind:value={answers[q.id]}
												rows="3"
												placeholder="Votre réponse…"
												class="w-full rounded-lg border border-slate-300 px-3 py-2 text-xs text-slate-800 focus:border-teal-500 focus:outline-none focus:ring-1 focus:ring-teal-500"
											></textarea>
										{/if}
									</div>
								</div>
							</div>
						</div>
					{/each}
				</div>

				<div class="border-t border-slate-100 bg-slate-50 px-7 py-5">
					{#if submitError}
						<div class="mb-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-medium text-rose-800">
							{submitError}
						</div>
					{/if}
					<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
						<p class="text-[11px] text-slate-500">
							{#if unanswered() > 0}
								{unanswered()} question(s) sans réponse — elles seront transmises vides.
							{:else}
								Toutes les questions sont renseignées.
							{/if}
							<br />Une fois transmise, votre évaluation ne pourra plus être modifiée.
						</p>
						<button
							type="button"
							on:click={submit}
							disabled={submitting || form.questions.length === unanswered()}
							class="shrink-0 rounded-lg bg-teal-600 px-6 py-2.5 text-xs font-bold text-white shadow-sm transition-colors hover:bg-teal-700 disabled:opacity-50"
						>
							{submitting ? 'Envoi en cours…' : 'Transmettre mon évaluation'}
						</button>
					</div>
				</div>
			</div>

			<p class="mt-5 text-center text-[11px] text-slate-400">
				Wetchah GRC — Contrôle de gestion, risques et conformité
			</p>
		{/if}
	</div>
</div>
