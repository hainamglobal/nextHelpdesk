import { computed, ref } from "vue";
import { defineStore } from "pinia";

export const useTicketStatusStore = defineStore("ticketStatus", () => {
  const options = ref(["Open", "Replied", "Resolved", "Closed"]);
  const labelMap: Record<string, string> = {
    Open: "Đang mở",
    Replied: "Đã phản hồi",
    Resolved: "Đã giải quyết",
    Closed: "Đã đóng",
  };
  const dropdown = computed(() =>
    options.value.map((o) => ({
      label: labelMap[o] || o,
      value: o,
    }))
  );
  const colorMap: Record<string, string> = {
    Open: "red",
    Replied: "blue",
    Resolved: "green",
    Closed: "gray",
  };
  const stateActive = ["Open", "Replied"];
  const stateInactive = ["Resolved", "Closed"];

  return {
    colorMap,
    dropdown,
    labelMap,
    options,
    stateActive,
    stateInactive,
  };
});
