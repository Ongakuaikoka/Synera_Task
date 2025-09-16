<script setup lang="ts">
import { computed, ref } from 'vue'
import { PaperAirplaneIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const props = defineProps<{
  isLoading: boolean
}>()

const emit = defineEmits<{
  sendMessage: [content: string]
}>()

const message = ref('')

const onSubmit = () => {
  if (!message.value) return

  emit('sendMessage', message.value)
  message.value = ''
}

const submitBtnClasses = computed(() =>
  props.isLoading
    ? ['bg-emerald-300']
    : ['bg-emerald-500', 'hover:bg-emerald-400', 'cursor-pointer'],
)
</script>

<template>
  <div
    class="bg-white w-full rounded-lg p-1 sm:p-2 flex items-stretch gap-1 sm:gap-2 input-wrapper min-w-0"
  >
    <textarea
      v-model.trim="message"
      rows="3"
      placeholder="Enter your message here..."
      :disabled="isLoading"
      class="flex-1 min-w-0"
    ></textarea>
    <button 
      type="button"
      @click="onSubmit"
      class="w-18 flex items-center justify-center text-white rounded-lg flex-shrink-0"
      :class="submitBtnClasses"
    >
      <ArrowPathIcon v-if="isLoading" class="w-8 animate-spin" />
      <PaperAirplaneIcon v-else class="w-8" />
    </button>
  </div>
</template>

<style scoped>
textarea {
  resize: none;
}

textarea:focus {
  border: none !important;
  outline: none !important;
}

.input-wrapper:focus-within {
  outline: solid 1px var(--color-cyan-700);
}
</style>
