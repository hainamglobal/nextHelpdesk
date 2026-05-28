<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.agents')">
      <template #right>
        <Button
          :label="$t('agents.new_agent')"
          theme="gray"
          variant="solid"
          @click="isDialogVisible = !isDialogVisible"
        >
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </PageTitle>
    <ListView
      :columns="columns"
      :resource="agents"
      :empty-message="emptyMessage"
      class="mt-2.5"
      doctype="HD Agent"
    >
      <template #name="{ data }">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Avatar :label="data.name" :image="data.user_image" size="sm" />
            <div class="line-clamp-1">{{ data.full_name }}</div>
          </div>
          <Badge
            v-if="!data.is_active"
            size="md"
            theme="orange"
            variant="subtle"
            >{{ $t('agents.inactive') }}</Badge
          >
        </div>
      </template>
      <template #row-extra="{ data }">
        <div class="cursor-pointer text-xs" @click="toTickets(data.name)">
          {{ $t('agents.tickets') }} &rightarrow;
        </div>
      </template>
    </ListView>
    <AddNewAgentsDialog
      :show="isDialogVisible"
      @close="isDialogVisible = false"
    />
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { usePageMeta, Avatar, Badge } from "frappe-ui";
import { AGENT_PORTAL_TICKET_LIST } from "@/router";
import { createListManager } from "@/composables/listManager";
import { useFilter } from "@/composables/filter";
import AddNewAgentsDialog from "@/components/desk/global/AddNewAgentsDialog.vue";
import PageTitle from "@/components/PageTitle.vue";
import { ListView } from "@/components";

const { t } = useI18n();
const { apply, storage } = useFilter("HD Ticket");
const isDialogVisible = ref(false);
const emptyMessage = computed(() => t("agents.empty"));
const columns = computed(() => [
  {
    label: t("common.name"),
    key: "name",
    width: "w-80",
  },
  {
    label: t("common.email"),
    key: "email",
    width: "w-80",
  },
  {
    label: t("common.username"),
    key: "username",
    width: "w-80",
  },
]);

const agents = createListManager({
  doctype: "HD Agent",
  fields: [
    "name",
    "is_active",
    "user.full_name",
    "user.user_image",
    "user.email",
    "user.username",
  ],
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = () => toTickets(d.name);
    }
    return data;
  },
});

usePageMeta(() => {
  return {
    title: t("sidebar.agents"),
  };
});

function toTickets(user: string) {
  storage.value.clear();
  storage.value.add({
    fieldname: "_assign",
    operator: "is",
    value: user,
  });
  apply({
    name: AGENT_PORTAL_TICKET_LIST,
  });
}
</script>
