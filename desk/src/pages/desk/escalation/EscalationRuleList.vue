<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.escalation_rules')">
      <template #right>
        <Button
          :label="$t('escalation_rules.new_rule')"
          theme="gray"
          variant="solid"
          @click="openDialog(null)"
        >
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </PageTitle>
    <ListView
      :columns="columns"
      :resource="rules"
      :empty-message="emptyMessage"
      class="mt-2.5"
      doctype="HD Escalation Rule"
    >
      <template #is_enabled="{ data }">
        <Badge :theme="data.is_enabled ? 'green' : 'red'" variant="subtle">
          {{ data.is_enabled ? $t("escalation_rules.enabled") : $t("escalation_rules.disabled") }}
        </Badge>
      </template>
      <template #ticket_type="{ data }">
        {{ ticketTypeLabelMap[data.ticket_type] || data.ticket_type }}
      </template>
    </ListView>
    <EscalationRuleDialog
      v-if="showDialog"
      v-model="showDialog"
      :name="selectedRule"
    />
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { usePageMeta, Badge } from "frappe-ui";
import { socket } from "@/socket";
import { createListManager } from "@/composables/listManager";
import { ListView } from "@/components";
import PageTitle from "@/components/PageTitle.vue";
import EscalationRuleDialog from "./EscalationRuleDialog.vue";

const { t } = useI18n();
const showDialog = ref(false);
const selectedRule = ref(null);
const emptyMessage = computed(() => t("escalation_rules.empty"));

// Map loại phiếu sang tiếng Việt
const ticketTypeLabelMap: Record<string, string> = {
  Bug: "Lỗi",
  Incident: "Sự cố",
  Question: "Câu hỏi",
  Unspecified: "Chưa xác định",
};

const columns = computed(() => [
  {
    label: t("escalation_rules.priority"),
    key: "priority",
    width: "w-64",
  },
  {
    label: t("escalation_rules.team"),
    key: "team",
    width: "w-64",
  },
  {
    label: t("escalation_rules.ticket_type"),
    key: "ticket_type",
    width: "w-64",
  },
  {
    label: t("escalation_rules.status"),
    key: "is_enabled",
    width: "w-20",
  },
]);

const rules = createListManager({
  doctype: "HD Escalation Rule",
  fields: ["name", "priority", "team", "ticket_type", "is_enabled"],
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = () => openDialog(d.name);
    }
    return data;
  },
});

usePageMeta(() => {
  return {
    title: t("sidebar.escalation_rules"),
  };
});

function openDialog(rule: string | null) {
  selectedRule.value = rule;
  showDialog.value = true;
}

socket.on("helpdesk:new-escalation-rule", () => rules.reload());
socket.on("helpdesk:delete-escalation-rule", () => rules.reload());
</script>
