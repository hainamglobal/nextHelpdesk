<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.tickets')">
      <template #right>
        <div class="flex gap-2">
          <div
            class="flex items-center justify-between text-base text-gray-700"
          >
            <div class="flex gap-4">
              <Dropdown :options="dropdownOptions">
                <template #default="{ open }">
                  <Button
                    :label="dropdownTitle"
                    :icon-right="open ? 'chevron-up' : 'chevron-down'"
                    theme="gray"
                    variant="outline"
                  />
                </template>
              </Dropdown>
            </div>
          </div>
          <RouterLink
            v-if="!configStore.preferKnowledgeBase"
            :to="{ name: CUSTOMER_PORTAL_NEW_TICKET }"
          >
            <Button
              class="bg-gray-900 text-white hover:bg-gray-800"
              :label="$t('tickets.new_ticket')"
              icon-right="plus"
            />
          </RouterLink>
        </div>
      </template>
    </PageTitle>
    <ListView
      :columns="columns"
      :resource="tickets"
      class="mt-2.5"
      doctype="HD Ticket"
    >
      <template #status="{ data }">
        <Badge
          :label="transformStatus(data.status)"
          :theme="ticketStatusStore.colorMap[data.status]"
          variant="outline"
        />
      </template>
      <template #creation="{ data }">
        {{ dayjs(data.creation).fromNow() }}
      </template>
    </ListView>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { Dropdown } from "frappe-ui";
import { dayjs } from "@/dayjs";
import { useConfigStore } from "@/stores/config";
import { useTicketStatusStore } from "@/stores/ticketStatus";
import { createListManager } from "@/composables/listManager";
import { CUSTOMER_PORTAL_TICKET, CUSTOMER_PORTAL_NEW_TICKET } from "@/router";
import { ListView } from "@/components";
import PageTitle from "@/components/PageTitle.vue";

const configStore = useConfigStore();
const ticketStatusStore = useTicketStatusStore();
const columns = [
  {
    label: "#",
    key: "name",
    width: "w-12",
  },
  {
    label: "Tiêu đề",
    key: "subject",
    width: "w-96",
  },
  {
    label: "Trạng thái",
    key: "status",
    width: "w-32",
  },
  {
    label: "Ngày tạo",
    key: "creation",
    width: "w-32",
  },
];

const tickets = createListManager({
  doctype: "HD Ticket",
  pageLength: 20,
  fields: ["name", "creation", "subject", "status"],
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = {
        name: CUSTOMER_PORTAL_TICKET,
        params: {
          ticketId: d.name,
        },
      };
    }
  },
});

const ACTIVE_TICKET_TYPES = ["Open", "Replied"];
const dropdownTitle = ref("Tất cả phiếu");
const dropdownOptions = [
  {
    label: "Tất cả phiếu",
    onClick() {
      filter("Tất cả phiếu", { status: undefined });
    },
  },
  {
    label: "Phiếu đang mở",
    onClick() {
      filter("Phiếu đang mở", { status: ["in", ACTIVE_TICKET_TYPES] });
    },
  },
  {
    label: "Phiếu đã đóng",
    onClick() {
      filter("Phiếu đã đóng", { status: ["not in", ACTIVE_TICKET_TYPES] });
    },
  },
];

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function filter(title: string, filters: Record<string, any>) {
  tickets.update({
    ...tickets,
    filters: {
      ...tickets.filters,
      ...filters,
    },
  });
  tickets.reload();
  dropdownTitle.value = title;
}

function transformStatus(status: string) {
  const statusMap: Record<string, string> = {
    Open: "Đang mở",
    Replied: "Chờ phản hồi",
    Resolved: "Đã giải quyết",
    Closed: "Đã đóng",
  };
  return statusMap[status] || status;
}
</script>
