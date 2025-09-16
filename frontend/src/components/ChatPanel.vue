<script setup lang="ts">
import { computed, inject, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import ChatInput from './ChatInput.vue'
import MessageBubble from './MessageBubble.vue'
import type { Message } from '@/domain/message'
import { ChatClientKey } from '@/infrastructure/chat-client'

const props = defineProps<{ conversationId: string }>()
const emit = defineEmits<{ 'first-response': [] }>()

const chatClient = inject(ChatClientKey)!
const messages = ref<Message[]>([])
const scrollContainer = ref<HTMLElement>()
let unsubscribe: (() => void) | null = null
let sawFirstAI = ref(false)

const init = async () => {
  messages.value = await chatClient.getConversationHistory(props.conversationId)
  sawFirstAI.value = messages.value.some(m => m.sender !== 'You')
  unsubscribe?.()
  unsubscribe = chatClient.subscribe(props.conversationId, onReceiveMessage)
}

onMounted(init)
watch(() => props.conversationId, init)
onBeforeUnmount(() => unsubscribe?.())

const onSendMessage = async (content: string) => {
  await chatClient.sendConversationMessage(props.conversationId, content)
}

const onReceiveMessage = (m: Message) => {
  messages.value.push(m)
  if (!sawFirstAI.value && m.sender !== 'You') {
    sawFirstAI.value = true
    emit('first-response')
  }
}

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    scrollContainer.value?.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  },
)

const isLoading = computed(() => messages.value.at(-1)?.sender === 'You')
</script>

<template>
  <div class="flex-1 flex flex-col gap-4 min-w-0 min-h-0">
    <div ref="scrollContainer" class="flex-1 min-h-0 overflow-y-auto flex flex-col gap-4 pr-4">
      <div v-if="messages.length === 0" class="flex-1 grid place-items-center text-center text-gray-500">
        Start the conversation by sending a message.
      </div>
      <MessageBubble v-for="message in messages" :key="message.id" :message="message" />
    </div>
    <ChatInput @send-message="onSendMessage" :is-loading="isLoading" />
  </div>
</template>

<style scoped></style>
