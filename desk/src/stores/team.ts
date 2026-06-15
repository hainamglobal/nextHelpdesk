import { computed, ComputedRef } from "vue";
import { defineStore } from "pinia";
import { createListResource } from "frappe-ui";

type Team = {
	name: string;
};

export const useTeamStore = defineStore("team", () => {
	const d__ = createListResource({
		doctype: "HD Team",
		auto: true,
		pageLength: 99999,
	});

	const labelMap: Record<string, string> = {
		"Billing": "Thanh toán",
		"Product Experts": "Chuyên gia sản phẩm",
	};

	const options: ComputedRef<Array<Team>> = computed(
		() => d__.list?.data || []
	);

	const dropdown = computed(() =>
		options.value.map((i) => ({
			label: labelMap[i.name] || i.name,
			value: i.name,
		}))
	);

	return {
		dropdown,
		labelMap,
		options,
	};
});
