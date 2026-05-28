<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.ticket_types')">
      <template #right>
        <RouterLink :to="{ name: AGENT_PORTAL_TICKET_TYPE_NEW }">
          <Button :label="$t('ticket_types.new_type')" theme="gray" variant="solid">
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </RouterLink>
      </template>
    </PageTitle>
    <ListView
      :columns="columns"
      :resource="ticketTypes"
      :empty-message="emptyMessage"
      class="mt-2.5"
      doctype="HD Ticket Type"
    />
  </div>
</template>
<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { usePageMeta } from "frappe-ui";
import {
  AGENT_PORTAL_TICKET_TYPE_NEW,
  AGENT_PORTAL_TICKET_TYPE_SINGLE,
} from "@/router";
import { createListManager } from "@/composables/listManager";
import PageTitle from "@/components/PageTitle.vue";
import { ListView } from "@/components";

const { t } = useI18n();
const emptyMessage = computed(() => t("ticket_types.empty"));
const columns = computed(() => [
  {
    label: t("common.name"),
    key: "name",
    width: "w-80",
  },
  {
    label: t("common.priority"),
    key: "priority",
    width: "w-80",
  },
]);

const ticketTypes = createListManager({
  doctype: "HD Ticket Type",
  fields: ["name", "priority"],
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = {
        name: AGENT_PORTAL_TICKET_TYPE_SINGLE,
        params: {
          id: d.name,
        },
      };
    }
    return data;
  },
});

usePageMeta(() => {
  return {
    title: t("sidebar.ticket_types"),
  };
});
</script>
