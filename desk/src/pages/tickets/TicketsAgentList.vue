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
    <template #custom_severity="{ data }">
      <Badge
        v-if="data.custom_severity"
        :label="severityLabelMap[data.custom_severity] || data.custom_severity"
        :theme="severityColorMap[data.custom_severity] || 'gray'"
        variant="subtle"
      />
      <span v-else>⸺</span>
    </template>
    <template #ticket_type="{ data }">
      {{ ticketTypeLabelMap[data.ticket_type] || data.ticket_type }}
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
    <template #customer="{ data }">
      <div class="flex flex-col">
        <span class="font-medium text-gray-900 truncate" :title="getDisplayName(data)">
          {{ getDisplayName(data) }}
        </span>
        <span class="text-xs text-gray-500 truncate" :title="getEmail(data.raised_by)">
          {{ getEmail(data.raised_by) }}
        </span>
      </div>
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
import { useAuthStore } from "@/stores/auth";
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
const authStore = useAuthStore();
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

// Map loại phiếu sang tiếng Việt
const ticketTypeLabelMap: Record<string, string> = {
  Bug: "Lỗi",
  Incident: "Sự cố",
  Question: "Câu hỏi",
  Unspecified: "Chưa xác định",
};

// Map mức độ nghiêm trọng sang tiếng Việt & màu sắc
const severityLabelMap: Record<string, string> = {
  Urgent: "Khẩn cấp",
  High: "Cao",
  Medium: "Trung bình",
  Low: "Thấp",
  "Khẩn cấp": "Khẩn cấp",
  "Cao": "Cao",
  "Trung bình": "Trung bình",
  "Thấp": "Thấp",
};

const severityColorMap: Record<string, string> = {
  Low: "green",
  Medium: "orange",
  High: "red",
  Urgent: "red",
  "Thấp": "green",
  "Trung bình": "orange",
  "Cao": "red",
  "Khẩn cấp": "red",
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

function getDisplayName(data: any) {
  if (data.full_name) return data.full_name;
  if (data.customer_name) return data.customer_name;
  if (data.contact) {
    if (typeof data.contact === "string") return data.contact;
    if (data.contact.full_name) return data.contact.full_name;
    if (data.contact.name) return data.contact.name;
  }
  
  // Try to parse name from raised_by (e.g. "John Doe <john@doe.com>")
  if (data.raised_by) {
    const match = data.raised_by.match(/^(.*?)\s*<.*>$/);
    if (match && match[1]) {
      const name = match[1].replace(/["']/g, "").trim();
      if (name) return name;
    }
  }
  
  if (data.customer) return data.customer;
  
  // Fallback to email prefix if no name found
  if (data.raised_by) {
    const email = getEmail(data.raised_by);
    return email.split('@')[0];
  }
  return "Không rõ";
}

function getEmail(raisedBy: string) {
  if (!raisedBy) return "";
  const match = raisedBy.match(/<([^>]+)>/);
  return match ? match[1] : raisedBy;
}

function assignOpts(selected: Set<number>) {
  // Loại bỏ các ticket không thuộc quyền thao tác của user hiện tại
  const validSelectedIds = Array.from(selected).filter(ticketId => {
    const ticket = props.resource?.data?.find((t: any) => t.name === ticketId);
    if (!ticket) return false;
    // Nếu là Admin thì thao tác được tất cả
    if (authStore.isAdmin) return true;
    
    // Được phép thao tác nếu ticket chưa gán cho ai (để nhận) 
    // hoặc đã gán cho chính user hiện tại
    const isUnassigned = !ticket._assign || ticket._assign === '[]' || ticket._assign === '';
    const isMine = ticket._assign && ticket._assign.includes(authStore.userId);
    return isUnassigned || isMine;
  });

  return agentStore.options.map((a) => ({
    label: a.agent_name,
    onClick: () => {
      if (validSelectedIds.length === 0) {
        createToast({ title: "Không có phiếu hợp lệ để phân công", icon: "x", iconClasses: "text-red-500" });
        return;
      }
      bulkAssignTicketToAgent.submit({
        ticket_ids: validSelectedIds,
        agent_id: a.name,
      });
    }
  }));
}
</script>
