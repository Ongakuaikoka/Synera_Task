<script setup lang="ts">
import { computed, inject, nextTick, onMounted, ref, watch } from 'vue'
import ChatInput from './ChatInput.vue'
import MessageBubble from './MessageBubble.vue'
import type { Message } from '@/domain/message'
import { ChatClientKey } from '@/infrastructure/chat-client'

const chatClient = inject(ChatClientKey)!
const messages = ref<Message[]>([])
const scrollContainer = ref<HTMLElement>()

onMounted(async () => {
  messages.value = await chatClient.getMessageHistory()
  chatClient.subscribe(onReceiveMessage)
})

const onSendMessage = async (content: string) => {
  await chatClient.sendMessage(content)
}

const onReceiveMessage = (newMessage: Message) => {
  messages.value.push(newMessage)
}

watch(
  () => messages.value.length,
  async () => {
    await nextTick() // Ensure the DOM is updated before scrolling to the bottom.
    scrollContainer.value?.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  },
)

const isLoading = computed(() => {
  if (messages.value.length === 0) return false

  return messages.value[messages.value.length - 1].sender === 'You'
})
</script>

<template>
  <div class="flex-1 flex flex-col gap-4 min-w-0">
    <div class="flex-1 flex flex-col gap-4 overflow-y-scroll pr-4 min-w-0" ref="scrollContainer">
      <div v-if="messages.length === 0" class="flex-1 content-center text-center">
        Welcome to Chatbot Bob! Start a new conversation by sending a message.
      </div>
      <MessageBubble v-for="message in messages" :key="message.id" :message />
    </div>
    <ChatInput @send-message="onSendMessage" :is-loading />
  </div>
</template>

<style scoped></style>
