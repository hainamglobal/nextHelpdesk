<template>
  <Dialog v-bind="attrs" :options="{ title: $t('kb.new_category') }">
    <template #body-content>
      <form @submit.prevent="newCategoryRes.submit">
        <div class="space-y-4">
          <div class="space-y-2">
            <div class="text-xs text-gray-700">{{ $t('kb.title_label') }}</div>
            <div class="flex items-center gap-2">
              <KnowledgeBaseIconSelector
                :icon="newCategoryIcon"
                @select="(icon) => (newCategoryIcon = icon)"
              />
              <FormControl
                v-model="newCategoryName"
                :placeholder="$t('kb.title_placeholder')"
                type="text"
              />
            </div>
          </div>
          <div class="space-y-2">
            <div class="text-xs text-gray-700">{{ $t('kb.description_label') }}</div>
            <FormControl
              v-model="newCategoryDescription"
              :placeholder="$t('kb.description_placeholder')"
              type="textarea"
            />
          </div>
          <Button class="w-full" :label="$t('kb.create')" theme="gray" variant="solid" />
        </div>
      </form>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, useAttrs } from "vue";
import { useI18n } from "vue-i18n";
import { createResource, Button, Dialog, FormControl } from "frappe-ui";
import KnowledgeBaseIconSelector from "./KnowledgeBaseIconSelector.vue";

interface E {
  (event: "success", id: string): void;
}

const attrs = useAttrs();
const emit = defineEmits<E>();
const { t } = useI18n();
const newCategoryName = ref("");
const newCategoryDescription = ref("");
const newCategoryIcon = ref("");
const newCategoryRes = createResource({
  url: "frappe.client.insert",
  makeParams() {
    return {
      doc: {
        doctype: "HD Article Category",
        category_name: newCategoryName.value,
        description: newCategoryDescription.value,
        icon: newCategoryIcon.value,
      },
    };
  },
  validate(params) {
    const requiredFields = [
      { field: "category_name", label: t("kb.title_label") },
      { field: "description", label: t("kb.description_label") },
      { field: "icon", label: "Icon" },
    ];
    for (const f of requiredFields) {
      if (!params.doc[f.field]) {
        return t("kb.required", { field: f.label });
      }
    }
  },
  onSuccess(data) {
    emit("success", data.name);
  },
});
</script>
