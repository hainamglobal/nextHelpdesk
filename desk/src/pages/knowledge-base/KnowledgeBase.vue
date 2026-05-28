<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.knowledge_base')" />
    <div class="flex grow border-t">
      <KnowledgeBaseSidebar />
      <RouterView :key="$route.fullPath" v-slot="{ Component }">
        <component :is="Component" v-if="Component" />
        <EmptyMessage v-else :message="$t('kb.select_category')" />
      </RouterView>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { usePageMeta } from "frappe-ui";
import PageTitle from "@/components/PageTitle.vue";
import EmptyMessage from "@/components/EmptyMessage.vue";
import KnowledgeBaseSidebar from "./KnowledgeBaseSidebar.vue";

const { t } = useI18n();

usePageMeta(() => {
  return {
    title: t("sidebar.knowledge_base"),
  };
});
</script>
