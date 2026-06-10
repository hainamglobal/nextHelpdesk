import { computed, ComputedRef } from "vue";
import { defineStore } from "pinia";
import { createListResource, createResource } from "frappe-ui";

type Agent = {
  name: string;
  agent_name: string;
  is_active: boolean;
  user: string;
  user_image: string;
};

export const useAgentStore = defineStore("agent", () => {
  const d__ = createListResource({
    doctype: "HD Agent",
    fields: ["name", "agent_name", "is_active", "user", "user.user_image"],
    auto: true,
    pageLength: 99999,
  });

  const options: ComputedRef<Array<Agent>> = computed(
    () => d__.list?.data || []
  );

  const dropdown = computed(() =>
    options.value.map((o) => ({
      label: o.agent_name,
      value: o.name,
    }))
  );

  const deleteAgentResource = createResource({
    url: "helpdesk.api.agent.delete_agent",
  });

  const deleteAgent = (name: string) => {
    return deleteAgentResource.submit({ name }).then(() => {
      d__.reload(); // also reload store's data if needed
    });
  };

  return {
    dropdown,
    options,
    deleteAgent,
  };
});
