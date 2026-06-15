<template>
  <div class="flex flex-col">
    <div class="border-l">
      <span>
        <TicketSidebarHeader :title="t('ticket_details.title')" />
        <div class="mx-5 my-6 flex flex-col justify-between gap-3.5 text-base">
          <div class="space-y-1.5">
            <span class="block text-sm text-gray-700">{{ t('ticket_details.id') }}</span>
            <span class="block break-words font-medium text-gray-900">
              {{ data.name }}
            </span>
          </div>
          <div v-if="data.customer" class="space-y-1.5">
            <span class="block text-sm text-gray-700">{{ t('ticket_details.customer') }}</span>
            <span class="block break-words font-medium text-gray-900">
              {{ data.customer }}
            </span>
          </div>
          <div class="space-y-1.5">
            <span class="block text-sm text-gray-700">{{ t('ticket_details.first_response') }}</span>
            <span class="mr-2 font-medium text-gray-900">
              {{ dayjs(data.first_responded_on || data.response_by).short() }}
            </span>
            <Badge
              v-if="!data.first_responded_on"
              :label="t('ticket_details.due')"
              theme="orange"
              variant="outline"
            />
            <Badge
              v-else-if="
                dayjs(data.first_responded_on).isBefore(dayjs(data.response_by))
              "
              :label="t('ticket_details.fulfilled')"
              theme="green"
              variant="outline"
            />
            <Badge v-else :label="t('ticket_details.failed')" theme="red" variant="outline" />
          </div>
          <div
            v-if="data.resolution_date || data.resolution_by"
            class="space-y-1.5"
          >
            <span class="block text-sm text-gray-700">{{ t('ticket_details.resolution') }}</span>
            <span class="mr-2 font-medium text-gray-900">
              {{ dayjs(data.resolution_date || data.resolution_by).short() }}
            </span>
            <Badge
              v-if="!data.resolution_date"
              :label="t('ticket_details.due')"
              theme="orange"
              variant="outline"
            />
            <Badge
              v-else-if="
                dayjs(data.resolution_date).isBefore(data.resolution_by)
              "
              :label="t('ticket_details.fulfilled')"
              theme="green"
              variant="outline"
            />
            <Badge v-else :label="t('ticket_details.failed')" theme="red" variant="outline" />
          </div>
          <div class="space-y-1.5">
            <span class="block text-sm text-gray-700">{{ t('ticket_details.modified') }}</span>
            <Tooltip :text="dayjs(ticket.data.modified).long()">
              <span class="block break-words font-medium text-gray-900">
                {{ dayjs(ticket.data.modified).fromNow() }}
              </span>
            </Tooltip>
          </div>
          <div class="space-y-1.5">
            <span class="block text-sm text-gray-700">{{ t('ticket_details.source') }}</span>
            <span class="block break-words font-medium text-gray-900">
              {{ ticket.data.via_customer_portal ? t('ticket_details.portal') : t('ticket_details.mail') }}
            </span>
          </div>
          <div v-if="data.feedback_rating" class="space-y-1.5">
            <span class="block text-sm text-gray-700">{{ t('ticket_details.feedback') }}</span>
            <StarRating :rating="data.feedback_rating" />
            <span class="block font-medium text-gray-900">
              {{ data.feedback_text }}
            </span>
            <span class="block text-gray-900">
              {{ data.feedback_extra }}
            </span>
          </div>
        </div>
      </span>
    </div>
    <div class="divider"></div>
    <div
      class="flex grow flex-col gap-3 truncate border-l p-5"
      :style="{
        'overflow-y': 'scroll',
      }"
    >
      <div v-for="o in options" :key="o.field" class="space-y-1.5">
        <span class="block text-sm text-gray-700">
          {{ o.label }}
        </span>
        <Autocomplete
          :options="o.store.dropdown"
          :placeholder="t('ticket_details.select_placeholder', { label: o.label.toLowerCase() })"
          :value="data[o.field] ? { label: o.store.labelMap?.[data[o.field]] || data[o.field], value: data[o.field] } : null"
          @change="update(o.field, $event.value)"
        />
      </div>
      <UniInput
        v-for="field in data.template.fields"
        :key="field.fieldname"
        :field="field"
        :value="data[field.fieldname]"
        @change="update(field.fieldname, $event.value)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject } from "vue";
import { createResource, Autocomplete, Tooltip } from "frappe-ui";
import { useI18n } from "vue-i18n";
import { dayjs } from "@/dayjs";
import { emitter } from "@/emitter";
import { createToast } from "@/utils";
import { useTeamStore } from "@/stores/team";
import { useTicketPriorityStore } from "@/stores/ticketPriority";
import { useTicketTypeStore } from "@/stores/ticketType";
import { useError } from "@/composables/error";
import { StarRating, UniInput } from "@/components";
import TicketSidebarHeader from "./TicketSidebarHeader.vue";
import { ITicket } from "./symbols";

const { t } = useI18n();
const ticket = inject(ITicket);
const data = computed(() => ticket.data);

const options = computed(() => [
  {
    field: "ticket_type",
    label: t("ticket_details.ticket_type"),
    store: useTicketTypeStore(),
  },
  {
    field: "priority",
    label: t("ticket_details.priority"),
    store: useTicketPriorityStore(),
  },
  {
    field: "agent_group",
    label: t("ticket_details.team"),
    store: useTeamStore(),
  },
]);

function update(fieldname: string, value: string) {
  createResource({
    url: "frappe.client.set_value",
    params: {
      doctype: "HD Ticket",
      name: data.value.name,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      emitter.emit("update:ticket");
      createToast({
        title: t("ticket_details.toast_updated"),
        icon: "check",
        iconClasses: "text-green-600",
      });
    },
    onError: useError(),
  });
}
</script>

<style scoped>
.divider {
  border-bottom: 1px solid #e2e2e2;
  border-style: dashed;
  position: relative;
}

.divider:before {
  position: absolute;
  bottom: -14px;
  left: 0;
  height: 28px;
  width: 14px;
  background: white;
  content: "";
  border-top-right-radius: 9999px;
  border-bottom-right-radius: 9999px;
  border-right-width: 1px;
  border-top-width: 1px;
  border-bottom-width: 1px;
}

.divider:after {
  position: absolute;
  bottom: -14px;
  left: 0;
  height: 28px;
  width: 14px;
  background: white;
  content: "";
  border-top-left-radius: 9999px;
  border-bottom-left-radius: 9999px;
  border-left-width: 1px;
  border-top-width: 1px;
  border-bottom-width: 1px;
}

.divider:after {
  right: 0;
  left: auto;
}
</style>
