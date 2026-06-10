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
      <template #action="{ data }">
        <Button
          variant="ghost"
          @click.stop="confirmDelete(data)"
        >
          <template #icon>
            <LucideX class="h-4 w-4 text-gray-500 hover:text-red-500" />
          </template>
        </Button>
      </template>
      <template #row-extra="{ data }">
        <div class="cursor-pointer text-xs" @click.stop="toTickets(data.name)">
          {{ $t('agents.tickets') }} &rightarrow;
        </div>
      </template>
    </ListView>
    <AddNewAgentsDialog
      :show="isDialogVisible"
      @close="isDialogVisible = false"
      @success="onAddAgents"
    />
    <Dialog v-model="showDelete" :options="deleteDialogOptions" />
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { usePageMeta, Avatar, Badge, Dialog, createResource } from "frappe-ui";
import { AGENT_PORTAL_TICKET_LIST } from "@/router";
import { createListManager } from "@/composables/listManager";
import { useFilter } from "@/composables/filter";
import AddNewAgentsDialog from "@/components/desk/global/AddNewAgentsDialog.vue";
import PageTitle from "@/components/PageTitle.vue";
import { ListView } from "@/components";

import { useAgentStore } from "@/stores/agent";

const { t } = useI18n();
const { apply, storage } = useFilter("HD Ticket");
const agentStore = useAgentStore();
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
  {
    label: "Thao tác",
    key: "action",
    width: "w-20",
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

const showDelete = ref(false);
const agentToDelete = ref<{ name: string; full_name?: string } | null>(null);

const deleteDialogOptions = ref({
  title: "Xóa Agent",
  message: "",
  actions: [
    {
      label: "Xác nhận",
      theme: "red",
      variant: "solid",
      onClick: () => {
        if (agentToDelete.value) {
          const nameToDelete = agentToDelete.value.name;
          return agentStore.deleteAgent(nameToDelete).then(() => {
            showDelete.value = false;
            agentToDelete.value = null;
            
            if (agents.data) {
              const idx = agents.data.findIndex((a: any) => a.name === nameToDelete);
              if (idx > -1) {
                agents.data.splice(idx, 1);
              }
            }
          });
        }
      },
    },
  ],
});

function confirmDelete(data: any) {
  agentToDelete.value = data;
  deleteDialogOptions.value.message = `Bạn có chắc chắn muốn xóa ${data.full_name || data.name}? Hành động này không thể hoàn tác!`;
  showDelete.value = true;
}

function onAddAgents(res: any) {
  // Ensure we get an array, unwrapping if necessary
  let newAgents = Array.isArray(res) ? res : (res && Array.isArray(res.message) ? res.message : []);
  
  if (newAgents && newAgents.length > 0) {
    if (!agents.data) {
      agents.data = [];
    }
    for (const agent of newAgents) {
      if (!agent) continue;
      
      // Normalize fields so they render correctly in the ListView columns
      agent.full_name = agent.full_name || agent.user || agent.name;
      agent.email = agent.email || agent.user;
      agent.username = agent.username || agent.user;
      agent.user_image = agent.user_image || '';
      agent.onClick = () => toTickets(agent.name);
      
      agents.data.unshift(agent);
    }
  }
}
</script>
