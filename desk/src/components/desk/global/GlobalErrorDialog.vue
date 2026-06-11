<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform -translate-y-full opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform -translate-y-full opacity-0"
    >
      <div
        v-if="globalErrorState.show"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-[99999] w-[90%] max-w-md bg-white rounded-lg shadow-2xl border border-red-100 overflow-hidden"
      >
        <div class="bg-red-50 px-4 py-3 border-b border-red-100 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <FeatherIcon name="alert-circle" class="w-4 h-4 text-red-600" />
            <h3 class="text-base font-semibold text-red-800">{{ globalErrorState.title }}</h3>
          </div>
          <button @click="globalErrorState.show = false" class="text-red-400 hover:text-red-600 transition-colors">
            <FeatherIcon name="x" class="w-4 h-4" />
          </button>
        </div>
        <div class="p-4 text-sm text-gray-700 leading-relaxed">
          {{ globalErrorState.message }}
        </div>
        <div class="bg-gray-50 px-4 py-3 flex justify-end">
          <Button appearance="secondary" @click="globalErrorState.show = false">
            Đóng
          </Button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { Button, FeatherIcon } from "frappe-ui";
import { globalErrorState } from "@/utils";
</script>
