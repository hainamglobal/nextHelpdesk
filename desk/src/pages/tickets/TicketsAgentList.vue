<template>
  <ListView
    :columns="columns"
    :resource="resource"
    doctype="HD Ticket"
    checkbox
    filter
  >
    <template #status="{ data }">
      <Badge
        :label="statusLabelMap[data.status] || data.status"
        :theme="ticketStatusStore.colorMap[data.status]"
        variant="subtle"
      />
    </template>
    <template #priority="{ data }">
      {{ priorityLabelMap[data.priority] || data.priority }}
    </template>
    <template #conversation="{ data }">
      <span class="flex items-center">
        <span v-for="i in ['incoming', 'outgoing', 'comments']" :key="i">
          <Tooltip v-if="data.conversation[i]" :text="capitalize(i)">
            <span class="mr-1 flex w-8 items-center gap-1">
              <LucideArrowDown v-if="i === 'incoming'" class="h-3 w-3" />
              <LucideArrowUp v-else-if="i === 'outgoing'" class="h-3 w-3" />
              <LucideMessageSquare v-else class="h-3 w-3" />
              <span class="">
                {{ data.conversation[i] }}
              </span>
            </span>
          </Tooltip>
        </span>
      </span>
    </template>
    <template #assignee="{ data }">
      <UserAvatar v-bind="data.assignee" expand />
    </template>
    <template #agreement_status="{ data }">
      <Badge
        :label="slaLabelMap[data.agreement_status] || data.agreement_status"
        :theme="slaStatusColorMap[data.agreement_status]"
        variant="outline"
      />
    </template>
    <template #response_by="{ data }">
      <span v-if="data.response_by">
        <Badge
          v-if="
            data.first_responded_on &&
            dayjs(data.first_responded_on).isBefore(data.response_by)
          "
          label="Đúng hạn"
          theme="green"
          variant="outline"
        />
        <Badge
          v-else-if="dayjs(data.first_responded_on).isAfter(data.response_by)"
          label="Trễ hạn"
          theme="red"
          variant="outline"
        />
        <Tooltip v-else :text="dayjs(data.response_by).long()">
          {{ dayjs(data.response_by).fromNow() }}
        </Tooltip>
      </span>
    </template>
    <template #resolution_by="{ data }">
      <span v-if="data.resolution_by">
        <Badge
          v-if="
            data.resolution_date &&
            dayjs(data.resolution_date).isBefore(data.resolution_by)
          "
          label="Đúng hạn"
          theme="green"
          variant="outline"
        />
        <Badge
          v-else-if="dayjs(data.resolution_date).isAfter(data.resolution_by)"
          label="Trễ hạn"
          theme="red"
          variant="outline"
        />
        <Tooltip v-else :text="dayjs(data.resolution_by).long()">
          {{ dayjs(data.resolution_by).fromNow() }}
        </Tooltip>
      </span>
    </template>
    <template #creation="{ data }">
      {{ dayjs(data.creation).fromNow() }}
    </template>
    <template #modified="{ data }">
      {{ dayjs(data.modified).fromNow() }}
    </template>
    <template #via_customer_portal="{ data }">
      {{ data.via_customer_portal ? "Cổng khách hàng" : "Email" }}
    </template>
    <template #actions="{ selection: s }">
      <Dropdown :options="assignOpts(s as Set<number>)">
        <template #default>
          <Button
            class="flex cursor-pointer items-center gap-1 text-gray-700"
            label="Phân công"
            theme="gray"
            variant="ghost"
          >
            <template #prefix>
              <Icon icon="lucide:user" class="h-4 w-4" />
            </template>
          </Button>
        </template>
      </Dropdown>
    </template>
  </ListView>
</template>

<script setup lang="ts">
import { capitalize } from "vue";
import { createResource, Badge, Dropdown, Tooltip } from "frappe-ui";
import { Icon } from "@iconify/vue";
import { dayjs } from "@/dayjs";
import { useAgentStore } from "@/stores/agent";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { createToast, getAssign } from "@/utils";
import { Resource } from "@/types";
import { useError } from "@/composables/error";
import { ListView, UserAvatar } from "@/components";

interface P {
  resource: Resource;
  columns: any[];
}

defineProps<P>();
const agentStore = useAgentStore();
const ticketStatusStore = useTicketStatusStore();
const slaStatusColorMap = {
  Fulfilled: "green",
  Failed: "red",
  "Resolution Due": "orange",
  "First Response Due": "orange",
  Paused: "blue",
};

// Map trạng thái sang tiếng Việt
const statusLabelMap: Record<string, string> = {
  Open: "Mở",
  Replied: "Đã phản hồi",
  Resolved: "Đã giải quyết",
  Closed: "Đóng",
};

// Map ưu tiên sang tiếng Việt
const priorityLabelMap: Record<string, string> = {
  Urgent: "Khẩn cấp",
  High: "Cao",
  Medium: "Trung bình",
  Low: "Thấp",
};

// Map giá trị API sang tiếng Việt
const slaLabelMap: Record<string, string> = {
  Fulfilled: "Đúng hạn",
  Failed: "Trễ hạn",
  "Resolution Due": "Sắp đến hạn giải quyết",
  "First Response Due": "Sắp đến hạn phản hồi",
  Paused: "Tạm dừng",
};

const bulkAssignTicketToAgent = createResource({
  url: "helpdesk.api.ticket.bulk_assign_ticket_to_agent",
  onSuccess: () => {
    createToast({
      title: "Phân công phiếu thành công",
      icon: "check",
      iconClasses: "text-green-500",
    });
  },
  onError: useError({ title: "Không thể phân công phiếu" }),
});

function assignOpts(selected: Set<number>) {
  return agentStore.options.map((a) => ({
    label: a.agent_name,
    onClick: () =>
      bulkAssignTicketToAgent.submit({
        ticket_ids: Array.from(selected),
        agent_id: a.name,
      }),
  }));
}
</script>
