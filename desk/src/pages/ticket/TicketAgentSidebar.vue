<template>
  <div class="flex">
    <TabGroup vertical>
      <TabPanels
        v-if="isExpanded"
        class="h-full"
        :style="{
          width: '310px',
        }"
      >
        <TabPanel v-for="item in items" :key="item.name" class="h-full">
          <component
            :is="item.component"
            class="h-full"
            @close="() => (isExpanded = false)"
          />
        </TabPanel>
      </TabPanels>
      <TabList
        class="sidebar flex flex-col gap-2 border-l"
        :style="{
          width: '50px',
          padding: '16px 12px 0 10px',
        }"
      >
        <Tab v-for="item in items" :key="item.name" v-slot="{ selected }">
          <Tooltip :text="item.name" placement="left">
            <div
              class="flex h-7 w-7 items-center justify-center rounded-full text-gray-900 transition-all"
              :class="{
                shadow: isExpanded && selected,
                'bg-gray-50': isExpanded && selected,
              }"
              @click="isExpanded = true"
            >
              <component :is="item.icon" class="h-4 w-4" />
            </div>
          </Tooltip>
        </Tab>
      </TabList>
    </TabGroup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { Tooltip } from "frappe-ui";
import { TabGroup, TabList, Tab, TabPanels, TabPanel } from "@headlessui/vue";
import { useI18n } from "vue-i18n";
import TicketActions from "./TicketActions.vue";
import TicketContact from "./TicketContact.vue";
import TicketDetails from "./TicketDetails.vue";
import TicketHistory from "./TicketHistory.vue";
import TicketViews from "./TicketViews.vue";
import LucideInfo from "~icons/lucide/info";
import LucideContact2 from "~icons/lucide/contact-2";
import LucideHistory from "~icons/lucide/history";
import LucideView from "~icons/lucide/view";
import LucidePointer from "~icons/lucide/pointer";

const { t } = useI18n();
const isExpanded = ref(true);
const items = computed(() => [
  {
    name: t("ticket_sidebar.details"),
    component: TicketDetails,
    icon: LucideInfo,
  },
  {
    name: t("ticket_sidebar.actions"),
    component: TicketActions,
    icon: LucidePointer,
  },
  {
    name: t("ticket_sidebar.contact"),
    component: TicketContact,
    icon: LucideContact2,
  },
  {
    name: t("ticket_sidebar.history"),
    component: TicketHistory,
    icon: LucideHistory,
  },
  {
    name: t("ticket_sidebar.views"),
    component: TicketViews,
    icon: LucideView,
  },
]);
</script>
