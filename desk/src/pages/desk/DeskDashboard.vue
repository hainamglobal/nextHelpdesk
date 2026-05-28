<template>
  <span>
    <PageTitle :title="$t('dashboard.title')">
      <template #right>
        <Tooltip v-if="!isEmpty(items.data)" placement="left" :text="$t('dashboard.date_info')">
          <div class="flex h-7 w-7 items-center justify-between">
            <IconInfo class="h-5 w-5 text-gray-700" />
          </div>
        </Tooltip>
      </template>
    </PageTitle>
    <div
      v-if="isEmpty(items.data)"
      class="flex grow select-none items-center justify-center text-base text-gray-700"
    >
      {{ $t("dashboard.empty") }}
    </div>
    <div v-else class="space-y-3 overflow-y-scroll p-5">
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <SingleString
          v-for="i in translatedItems.filter((i) => !i.is_chart)"
          :key="i.title"
          :title="i.title"
          :value="i.data"
        />
      </div>
      <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div
          v-for="i in translatedItems.filter((i) => i.is_chart)"
          :key="i.title"
          class="h-64 rounded border p-2"
        >
          <PieChart
            v-if="i.is_chart && i.chart_type === 'Pie'"
            :title="i.title"
            :data="i.data"
          />
          <LineChart
            v-else-if="i.is_chart && i.chart_type === 'Line'"
            :title="i.title"
            :data="i.data"
          />
        </div>
      </div>
    </div>
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { createResource, usePageMeta, Tooltip } from "frappe-ui";
import { isEmpty } from "lodash";
import PageTitle from "@/components/PageTitle.vue";
import LineChart from "@/components/charts/LineChart.vue";
import PieChart from "@/components/charts/PieChart.vue";
import SingleString from "@/components/charts/SingleString.vue";
import IconInfo from "~icons/espresso/alert-circle";

const { t } = useI18n();

const items = createResource({
  url: "helpdesk.api.dashboard.get_all",
  auto: true,
});

const titleKeys = {
  "Avg. first response time": "dashboard.avg_first_response_time",
  "Resolution within SLA": "dashboard.resolution_within_sla",
  "My tickets": "dashboard.my_tickets",
  "Status": "dashboard.status",
  "New tickets": "dashboard.new_tickets",
  "Type": "dashboard.type",
  "Activity": "dashboard.activity",
  "Priority": "dashboard.priority",
};

const nameKeys = {
  "open": "dashboard.open",
  "resolved": "dashboard.resolved",
  "closed": "dashboard.closed",
  "replied": "dashboard.replied",
  "low": "dashboard.low",
  "medium": "dashboard.medium",
  "high": "dashboard.high",
  "urgent": "dashboard.urgent",
  "unspecified": "dashboard.unspecified",
};

const valueReplacements = {
  "Hours": "dashboard.hours",
  "Not enough data": "dashboard.not_enough_data",
  "open": "dashboard.open",
  "replied": "dashboard.replied",
};

const translatedItems = computed(() => {
  if (!items.data) return [];
  return items.data.map((item) => {
    // Translate Title
    const titleKey = titleKeys[item.title];
    const translatedTitle = titleKey ? t(titleKey) : item.title;

    // Translate Data
    let translatedData = item.data;
    if (item.is_chart && Array.isArray(item.data)) {
      translatedData = item.data.map((d) => {
        const nameLower = d.name ? d.name.toLowerCase() : "";
        const nameKey = nameKeys[nameLower];
        return {
          ...d,
          name: nameKey ? t(nameKey) : d.name,
        };
      });
    } else if (typeof item.data === "string") {
      // Translate value like "8.0 Hours", "1 open", "not enough data"
      translatedData = item.data;
      for (const [englishWord, translationKey] of Object.entries(valueReplacements)) {
        const regex = new RegExp(`\\b${englishWord}\\b`, "gi");
        translatedData = translatedData.replace(regex, t(translationKey));
      }
    }

    return {
      ...item,
      title: translatedTitle,
      data: translatedData,
    };
  });
});

usePageMeta(() => {
  return {
    title: t("dashboard.title"),
  };
});
</script>
