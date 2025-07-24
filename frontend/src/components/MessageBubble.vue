<script setup lang="ts">
import type { Message } from '@/domain/message'
import { computed } from 'vue'

const props = defineProps<{
  message: Message
}>()

const formattedTimestamp = computed(() => {
  const date = new Date(props.message.timestamp)
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }
  return date.toLocaleString('de-DE', options).replace(',', '')
})
</script>

<template>
  <div
    class="flex flex-col gap-2 px-2 sm:px-4 py-2 rounded-lg w-full max-w-xs sm:max-w-md bg-white shadow-gray-200 shadow-2xs wrap-break-word"
    :class="{ 'ml-auto': message.sender === 'You' }"
  >
    <div>{{ message.content }}</div>
    <div class="text-gray-400 text-sm self-end">
      {{ message.sender }} - {{ formattedTimestamp }}
    </div>
  </div>
</template>

<style scoped></style>
