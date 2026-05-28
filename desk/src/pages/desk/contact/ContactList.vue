<template>
  <div class="flex flex-col">
    <PageTitle :title="$t('sidebar.contacts')">
      <template #right>
        <Button
          :label="$t('contacts.new_contact')"
          theme="gray"
          variant="solid"
          @click="isDialogVisible = !isDialogVisible"
        >
          <template #prefix>
            <LucidePlus class="h-4 w-4" />
          </template>
        </Button>
      </template>
    </PageTitle>
    <ListView
      :columns="columns"
      :resource="contacts"
      :empty-message="emptyMessage"
      class="mt-2.5"
      doctype="Contact"
    >
      <template #name="{ data }">
        <div class="flex items-center gap-2">
          <Avatar :label="data.name" :image="data.image" size="sm" />
          <div class="line-clamp-1">{{ data.name }}</div>
        </div>
      </template>
    </ListView>
    <NewContactDialog
      v-model="isDialogVisible"
      @contact-created="isDialogVisible = false"
    />
    <span v-if="isContactDialogVisible">
      <ContactDialog v-model="isContactDialogVisible" :name="selectedContact" />
    </span>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { usePageMeta, Avatar } from "frappe-ui";
import { createListManager } from "@/composables/listManager";
import NewContactDialog from "@/components/desk/global/NewContactDialog.vue";
import PageTitle from "@/components/PageTitle.vue";
import { ListView } from "@/components";
import ContactDialog from "./ContactDialog.vue";

const { t } = useI18n();
const isDialogVisible = ref(false);
const isContactDialogVisible = ref(false);
const selectedContact = ref(null);
const emptyMessage = computed(() => t("contacts.empty"));
const columns = computed(() => [
  {
    label: t("common.name"),
    key: "name",
    width: "w-80",
  },
  {
    label: t("common.email"),
    key: "email_id",
    width: "w-80",
  },
  {
    label: t("common.phone"),
    key: "phone",
    width: "w-80",
  },
]);

const contacts = createListManager({
  doctype: "Contact",
  fields: ["name", "email_id", "image", "phone"],
  auto: true,
  transform: (data) => {
    for (const d of data) {
      d.onClick = () => openContact(d.name);
    }
    return data;
  },
});

usePageMeta(() => {
  return {
    title: t("sidebar.contacts"),
  };
});

function openContact(id: string) {
  selectedContact.value = id;
  isContactDialogVisible.value = true;
}
</script>
