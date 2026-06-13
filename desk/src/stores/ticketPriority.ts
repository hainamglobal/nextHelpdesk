import { computed, ComputedRef } from "vue";
import { defineStore } from "pinia";
import { createListResource } from "frappe-ui";

type TicketPriority = {
  name: string;
  description: string;
};

export const useTicketPriorityStore = defineStore("ticketPriority", () => {
  const d__ = createListResource({
    doctype: "HD Ticket Priority",
    orderBy: "integer_value desc",
    auto: true,
    pageLength: 99999,
  });

  const labelMap: Record<string, string> = {
    Urgent: "Khẩn cấp",
    High: "Cao",
    Medium: "Trung bình",
    Low: "Thấp",
  };

  const options: ComputedRef<Array<TicketPriority>> = computed(
    () => d__.list?.data || []
  );
  const dropdown = computed(() =>
    options.value.map((o) => ({
      label: labelMap[o.name] || o.name,
      value: o.name,
    }))
  );
  const names = computed(() => options.value.map((o) => o.name));
  const colorMap: Record<string, string> = {
    Urgent: "red",
    High: "orange",
    Medium: "blue",
    Low: "green",
  };

  return {
    colorMap,
    dropdown,
    labelMap,
    names,
    options,
  };
});
