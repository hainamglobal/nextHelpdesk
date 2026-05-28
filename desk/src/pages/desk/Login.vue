<template>
	<div class="p-5">
		<div class="flex">
			<div>{{ $t('login.please_login') }}</div>
			<div class="ml-2">
				<Button @click="login">{{ $t('login.btn_login') }}</Button>
			</div>
		</div>
	</div>
</template>

<script>
export default {
	name: "Login",
	methods: {
		login() {
			window.location.replace("/login")
		},
	},
}
</script>

<style></style>
