<template>
	<keep-alive include="RecorderDetail">
		<router-view/>
	</keep-alive>
</template>

<script>
export default {
	name: "RecorderRoot",
	watch: {
		async $route() {
			netmanthan.router.current_route = await netmanthan.router.parse();
			netmanthan.breadcrumbs.update();
		}
	}
};
</script>
