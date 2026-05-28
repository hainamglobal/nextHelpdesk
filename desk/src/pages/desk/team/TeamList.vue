<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.teams')">
      <template #right>
        <Button
          :label="$t('teams.new_team')"
          theme="gray"
          variant="solid"
          @click="showNewDialog = !showNewDialog"
        >
          <template #prefix>
            <IconPlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </PageTitle>
    <ListView
      :columns="columns"
      :resource="teams"
      :empty-message="emptyMessage"
      class="mt-2.5"
      doctype="HD Team"
    />
    <Dialog
      v-model="showNewDialog"
      :options="{
        title: $t('teams.new_team'),
      }"
    >
      <template #body-content>
        <form class="space-y-2" @submit.prevent="newTeam.submit">
          <FormControl
            v-model="newTeamTitle"
            :label="$t('teams.title')"
            :placeholder="$t('teams.placeholder')"
            type="text"
          />
          <Button
            :disabled="isEmpty(newTeamTitle)"
            class="w-full"
            :label="$t('teams.create')"
            theme="gray"
            variant="solid"
          />
        </form>
      </template>
    </Dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { createResource, usePageMeta, Dialog, FormControl } from "frappe-ui";
import { isEmpty } from "lodash";
import { AGENT_PORTAL_TEAM_SINGLE } from "@/router";
import { createListManager } from "@/composables/listManager";
import { useError } from "@/composables/error";
import PageTitle from "@/components/PageTitle.vue";
import { ListView } from "@/components";
import IconPlus from "~icons/lucide/plus";

const router = useRouter();
const { t } = useI18n();
const showNewDialog = ref(false);
const newTeamTitle = ref(null);
const emptyMessage = computed(() => t("teams.empty"));
const columns = computed(() => [
  {
    label: t("common.name"),
    key: "name",
    width: "w-80",
  },
  {
    label: t("teams.assignment_rule"),
    key: "assignment_rule",
    width: "w-80",
  },
]);

const teams = createListManager({
  doctype: "HD Team",
  fields: ["name", "assignment_rule"],
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = {
        name: AGENT_PORTAL_TEAM_SINGLE,
        params: {
          teamId: d.name,
        },
      };
    }
    return data;
  },
});

const newTeam = createResource({
  url: "frappe.client.insert",
  makeParams() {
    return {
      doc: {
        doctype: "HD Team",
        team_name: newTeamTitle.value,
      },
    };
  },
  validate(params) {
    if (isEmpty(params.doc.team_name)) return t("teams.required");
  },
  auto: false,
  onSuccess() {
    router.replace({
      name: AGENT_PORTAL_TEAM_SINGLE,
      params: {
        teamId: newTeamTitle.value,
      },
    });
  },
  onError: useError({ title: t("teams.error") }),
});

usePageMeta(() => {
  return {
    title: t("sidebar.teams"),
  };
});
</script>
