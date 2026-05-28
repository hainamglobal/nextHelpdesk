<template>
  <div class="flex grow flex-col">
    <KnowledgeBaseCategoryHeader
      :title="subCategory.doc?.category_name"
      :description="subCategory.doc?.description"
    >
      <template #right>
        <div class="space-x-2">
          <Button
            :label="$t('kb.edit')"
            theme="gray"
            variant="outline"
            @click="showEdit = !showEdit"
          >
            <template #prefix>
              <IconEdit class="h-4 w-4" />
            </template>
          </Button>
          <Button
            :label="$t('kb.add_new')"
            theme="gray"
            variant="solid"
            @click="toNewArticle"
          >
            <template #prefix>
              <IconPlus class="h-4 w-4" />
            </template>
          </Button>
        </div>
      </template>
    </KnowledgeBaseCategoryHeader>
    <ListView :columns="columns" :resource="articles" doctype="HD Article">
      <template #title="{ data }">
        <div class="flex items-center gap-2">
          <IconFile class="h-4 w-4" />
          {{ data.title }}
        </div>
      </template>
      <template #status="{ data }">
        <Badge
          :theme="data.status === 'Published' ? 'green' : 'orange'"
          variant="subtle"
        >
          {{ data.status === 'Published' ? $t('kb.published') : $t('kb.draft') }}
        </Badge>
      </template>
      <template #emptyMessage>
        <EmptyMessage :message="$t('kb.empty_subcategory')" />
      </template>
    </ListView>
    <Dialog v-model="showEdit" :options="{ title: $t('kb.edit') }">
      <template #body-content>
        <form @submit.prevent="saveSubCategory">
          <div class="space-y-4">
            <FormControl
              v-model="newSubCategoryName"
              :placeholder="subCategory.doc.category_name"
              :label="$t('kb.name_label')"
              type="text"
            />
            <FormControl
              v-model="newSubCategoryDescription"
              :placeholder="subCategory.doc.description"
              :label="$t('kb.description_label')"
              type="textarea"
            />
            <Button
              :disabled="!newSubCategoryName && !newSubCategoryDescription"
              class="w-full"
              :label="$t('kb.save')"
              theme="gray"
              variant="solid"
            />
          </div>
        </form>
      </template>
    </Dialog>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import {
  createDocumentResource,
  debounce,
  Badge,
  Button,
  Dialog,
  FormControl,
} from "frappe-ui";
import { AGENT_PORTAL_KNOWLEDGE_BASE_ARTICLE } from "@/router";
import { createListManager } from "@/composables/listManager";
import { useError } from "@/composables/error";
import { ListView } from "@/components";
import KnowledgeBaseCategoryHeader from "./KnowledgeBaseCategoryHeader.vue";
import EmptyMessage from "@/components/EmptyMessage.vue";
import IconEdit from "~icons/lucide/edit-3";
import IconFile from "~icons/lucide/file-text";
import IconPlus from "~icons/lucide/plus";

const props = defineProps({
  subCategoryId: {
    type: String,
    required: true,
  },
});

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const newSubCategoryName = ref("");
const newSubCategoryDescription = ref("");
const showEdit = ref(false);

const subCategory = createDocumentResource({
  doctype: "HD Article Category",
  name: props.subCategoryId,
  auto: true,
  setValue: {
    onError: useError({ title: t("kb.toast_update_error") }),
  },
});

const saveSubCategory = debounce(
  () =>
    subCategory.setValue.submit({
      category_name: newSubCategoryName.value || subCategory.doc.category_name,
      description:
        newSubCategoryDescription.value || subCategory.doc.description,
    }),
  500
);

const articles = createListManager({
  doctype: "HD Article",
  filters: {
    category: props.subCategoryId,
  },
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = {
        name: AGENT_PORTAL_KNOWLEDGE_BASE_ARTICLE,
        params: {
          articleId: d.name,
        },
      };
    }
    return data;
  },
});

const columns = computed(() => [
  {
    label: t("kb.title_label"),
    key: "title",
    width: "w-96",
  },
  {
    label: t("kb.views"),
    key: "views",
    width: "w-12",
  },
  {
    label: t("kb.status"),
    key: "status",
    width: "w-40",
  },
]);

function toNewArticle() {
  router.push({
    name: AGENT_PORTAL_KNOWLEDGE_BASE_ARTICLE,
    params: {
      articleId: "new",
    },
    query: {
      category: route.params.categoryId,
      subCategory: route.params.subCategoryId,
    },
  });
}
</script>
