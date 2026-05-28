<template>
  <div
    class="z-0 flex select-none flex-col border-r border-gray-200 bg-gray-50 p-2 text-base duration-300 ease-in-out"
    :style="{
      'min-width': width,
      'max-width': width,
    }"
  >
    <UserMenu class="mb-2 ml-0.5" :options="profileSettings" />
    <span class="mb-4">
      <div
        v-if="!isExpanded && notificationStore.unread"
        class="absolute z-20 h-1.5 w-1.5 translate-x-6 translate-y-1 rounded-full bg-gray-800"
        theme="gray"
        variant="solid"
      />
      <SidebarLink
        class="relative"
        :label="t('sidebar.notifications')"
        :icon="LucideInbox"
        :on-click="() => notificationStore.toggle()"
        :is-expanded="isExpanded"
      >
        <template #right>
          <Badge
            v-if="isExpanded && notificationStore.unread"
            :label="notificationStore.unread"
            theme="gray"
            variant="subtle"
          />
        </template>
      </SidebarLink>
    </span>
    <div class="mb-4 flex flex-col gap-1">
      <SidebarLink
        v-for="option in menuOptions"
        v-bind="option"
        :key="option.label"
        :is-expanded="isExpanded"
        :is-active="option.to?.includes(route.name.toString())"
      />
    </div>
    <div class="flex flex-col gap-1">
      <SidebarLink
        v-for="option in extraOptions.filter((o) => !o.hide)"
        v-bind="option"
        :key="option.label"
        :is-expanded="isExpanded"
        :is-active="option.to?.includes(route.name?.toString())"
      />
    </div>
    <div class="grow" />
    <SidebarLink
      :icon="isExpanded ? LucideArrowLeftFromLine : LucideArrowRightFromLine"
      :is-active="false"
      :is-expanded="isExpanded"
      :label="isExpanded ? t('sidebar.collapse') : t('sidebar.expand')"
      :on-click="() => (isExpanded = !isExpanded)"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { storeToRefs } from "pinia";
import { useAuthStore } from "@/stores/auth";
import { useKeymapStore } from "@/stores/keymap";
import { useNotificationStore } from "@/stores/notification";
import { useSidebarStore } from "@/stores/sidebar";
import { useI18n } from "vue-i18n";
import {
  AGENT_PORTAL_AGENT_LIST,
  AGENT_PORTAL_CANNED_RESPONSE_LIST,
  AGENT_PORTAL_CONTACT_LIST,
  AGENT_PORTAL_CUSTOMER_LIST,
  AGENT_PORTAL_DASHBOARD,
  AGENT_PORTAL_ESCALATION_RULE_LIST,
  AGENT_PORTAL_TEAM_LIST,
  AGENT_PORTAL_TICKET_LIST,
  AGENT_PORTAL_TICKET_TYPE_LIST,
  CUSTOMER_PORTAL_LANDING,
} from "@/router";
import { SidebarLink } from "@/components";
import UserMenu from "./UserMenu.vue";
import LucideArrowUpFromLine from "~icons/lucide/arrow-up-from-line";
import LucideArrowRightFromLine from "~icons/lucide/arrow-right-from-line";
import LucideArrowLeftFromLine from "~icons/lucide/arrow-left-from-line";
import LucideBookOpen from "~icons/lucide/book-open";
import LucideCloudLightning from "~icons/lucide/cloud-lightning";
import LucideContact2 from "~icons/lucide/contact-2";
import LucideFolderOpen from "~icons/lucide/folder-open";
import LucideInbox from "~icons/lucide/inbox";
import LucideLayoutGrid from "~icons/lucide/layout-grid";
import LucideTicket from "~icons/lucide/ticket";
import LucideUser from "~icons/lucide/user";
import LucideUserCircle2 from "~icons/lucide/user-circle-2";
import LucideUsers from "~icons/lucide/users";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const keymapStore = useKeymapStore();
const notificationStore = useNotificationStore();
const { isExpanded, width } = storeToRefs(useSidebarStore());
const { t, locale } = useI18n();

const menuOptions = computed(() => [
  {
    label: t("sidebar.tickets"),
    icon: LucideTicket,
    to: AGENT_PORTAL_TICKET_LIST,
  },
  {
    label: t("sidebar.dashboard"),
    icon: LucideLayoutGrid,
    to: AGENT_PORTAL_DASHBOARD,
  },
  {
    label: t("sidebar.agents"),
    icon: LucideUser,
    to: AGENT_PORTAL_AGENT_LIST,
  },
  {
    label: t("sidebar.knowledge_base"),
    icon: LucideBookOpen,
    to: "DeskKBHome",
    isBeta: true,
  },
]);

const extraOptions = computed(() => [
  {
    label: t("sidebar.teams"),
    icon: LucideUsers,
    to: AGENT_PORTAL_TEAM_LIST,
  },
  {
    label: t("sidebar.escalation_rules"),
    icon: LucideArrowUpFromLine,
    to: AGENT_PORTAL_ESCALATION_RULE_LIST,
    isBeta: true,
  },
  {
    label: t("sidebar.ticket_types"),
    icon: LucideFolderOpen,
    to: AGENT_PORTAL_TICKET_TYPE_LIST,
    hide: true,
  },
  {
    label: t("sidebar.canned_responses"),
    icon: LucideCloudLightning,
    to: AGENT_PORTAL_CANNED_RESPONSE_LIST,
    isBeta: true,
  },
  {
    label: t("sidebar.customers"),
    icon: LucideUserCircle2,
    to: AGENT_PORTAL_CUSTOMER_LIST,
  },
  {
    label: t("sidebar.contacts"),
    icon: LucideContact2,
    to: AGENT_PORTAL_CONTACT_LIST,
  },
]);

const profileSettings = computed(() => [
  {
    label: t("sidebar.shortcuts"),
    icon: "command",
    onClick: () => keymapStore.toggleVisibility(true),
  },
  {
    label: t("sidebar.customer_portal"),
    icon: "users",
    onClick: () => {
      const path = router.resolve({ name: CUSTOMER_PORTAL_LANDING });
      window.open(path.href, "_blank");
    },
  },
  {
    label: locale.value === "vi" ? "English (EN)" : "Tiếng Việt (VI)",
    icon: "globe",
    onClick: () => {
      locale.value = locale.value === "vi" ? "en" : "vi";
      localStorage.setItem("locale", locale.value);
    },
  },
  {
    label: t("sidebar.logout"),
    icon: "log-out",
    onClick: () => authStore.logout(),
  },
]);
</script>
