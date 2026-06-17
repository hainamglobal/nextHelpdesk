import { useRoute } from "vue-router";
import { useStorage } from "@vueuse/core";

/**
 * @param doctype - The DocType to use
 * @param defaultHidden - Array of column keys to hide by default
 */
export function useColumns(doctype: string, defaultHidden: string[] = []) {
  const route = useRoute();
  const prefix = "hide_columns_v3";
  const storageKey = [prefix, route.path, doctype].join("_");
  
  // Convert default array to Set
  const defaultSet = new Set(defaultHidden);
  const storage = useStorage(storageKey, defaultSet);

  /**
   * @param key - The column key to toggle
   * @returns void
   * @description Toggles the column visibility
   */
  function toggle(key: string) {
    if (!storage.value.delete(key)) {
      storage.value.add(key);
    }
  }

  return {
    storage,
    toggle,
  };
}
