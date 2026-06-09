<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.tickets')">
      <template #right>
        <RouterLink :to="{ name: 'TicketAgentNew' }">
          <Button :label="$t('tickets.new_ticket')" theme="gray" variant="solid">
            <template #prefix>
              <LucidePlus class="h-4 w-4" />
            </template>
          </Button>
        </RouterLink>
      </template>
    </PageTitle>
    <div class="mx-5 mt-2.5 flex items-center justify-between">
      <PresetFilters doctype="HD Ticket" />
      <div class="flex items-center gap-2">
        <FilterPopover doctype="HD Ticket" />
        <Dropdown :options="sortOptions">
          <template #default>
            <Button :label="getOrder() || 'Sort'" variant="outline" size="sm">
              <template #prefix>
                <LucideArrowDownUp class="h-4 w-4" />
              </template>
            </Button>
          </template>
        </Dropdown>
        <ColumnSelector doctype="HD Ticket" :columns="columns" />
      </div>
    </div>
    <TicketsAgentList :resource="tickets" :columns="columns" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { createResource, usePageMeta, Button, Dropdown } from "frappe-ui";
import { AGENT_PORTAL_TICKET } from "@/router";
import { socket } from "@/socket";
import { useAuthStore } from "@/stores/auth";
import { useFilter } from "@/composables/filter";
import { useOrder } from "@/composables/order";
import { createListManager } from "@/composables/listManager";
import PageTitle from "@/components/PageTitle.vue";
import { ColumnSelector, FilterPopover } from "@/components";
import TicketsAgentList from "./TicketsAgentList.vue";
import PresetFilters from "./PresetFilters.vue";

const { t } = useI18n();
const route = useRoute();
const { userId, isAdmin } = useAuthStore();
const { getArgs, storage, add, apply, fields } = useFilter("HD Ticket");
const { get: getOrder, set: setOrder } = useOrder();
const pageLength = ref(20);
const tickets = createListManager({
  doctype: "HD Ticket",
  pageLength: pageLength.value,
  filters: getArgs(),
  orderBy: getOrder(),
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.class = {
        "font-medium": !d._seen?.includes(userId),
      };
      d.onClick = {
        name: AGENT_PORTAL_TICKET,
        params: {
          ticketId: d.name,
        },
      };
      d.conversation = {
        incoming: d.count_msg_incoming,
        outgoing: d.count_msg_outgoing,
        comments: d.count_comment,
      };
      d.source = d.via_customer_portal ? "Cổng khách hàng" : "Email";
    }
    return data;
  },
});

// Chỉ set filter mặc định khi chưa có query trên URL (lần đầu vào trang)
// Khi user xóa filter thủ công: URL sẽ có q="" → không ghi đè, tránh giật
onMounted(() => {
  if (route.query.q !== undefined) return; // user đã tự set hoặc xóa filter

  if (isAdmin.value) {
    // Admin: không filter, hiện tất cả
    return;
  }

  // User thường: set mặc định Assigned To = user hiện tại
  storage.value.clear();
  add({
    field: {
      label: "Assigned To",
      fieldname: "_assign",
      fieldtype: "Small Text",
      options: "",
    },
    fieldname: "_assign",
    operator: "like",
    value: userId.value,
  });
  apply();
});


const sortOptionsRes = createResource({
  url: "helpdesk.extends.doc.sort_options",
  auto: true,
  params: {
    doctype: "HD Ticket",
  },
});
const sortOptions = computed(() => {
  return sortOptionsRes.data?.map((o) => ({
    label: o,
    onClick: () => setOrder(o),
  }));
});

socket.on("helpdesk:new-ticket", () => {
  if (!tickets.hasPreviousPage) tickets.reload();
});

const columns = [
  {
    label: "#",
    key: "name",
    width: "w-10",
    text: "text-sm",
  },
  {
    label: "Tiêu đề",
    key: "subject",
    width: "w-96",
    text: "text-gray-900",
  },
  {
    label: "Trạng thái",
    key: "status",
    width: "w-20",
  },
  {
    label: "Ưu tiên",
    key: "priority",
    width: "w-32",
  },
  {
    label: "Loại",
    key: "ticket_type",
    width: "w-36",
  },
  {
    label: "Nhóm",
    key: "agent_group",
    width: "w-36",
  },
  {
    label: "Liên hệ",
    key: "contact",
    width: "w-36",
  },
  {
    label: "Thời hạn xử lý",
    key: "agreement_status",
    width: "w-36",
  },
  {
    label: "Phản hồi đầu tiên",
    key: "response_by",
    width: "w-32",
  },
  {
    label: "Giải quyết",
    key: "resolution_by",
    width: "w-32",
  },
  {
    label: "Khách hàng",
    key: "customer",
    width: "w-36",
  },
  {
    label: "Nguồn",
    key: "source",
    width: "w-36",
  },
  {
    label: "Người xử lý",
    key: "assignee",
    width: "w-40",
  },
  {
    label: "Hội thoại",
    key: "conversation",
    width: "w-28",
  },
  {
    label: "Cập nhật lần cuối",
    key: "modified",
    width: "w-32",
  },
  {
    label: "Ngày tạo",
    key: "creation",
    width: "w-36",
  },
];

usePageMeta(() => {
  return {
    title: t("sidebar.tickets"),
  };
});
</script>
