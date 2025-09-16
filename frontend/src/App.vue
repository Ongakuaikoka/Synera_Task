<script setup lang="ts">
import { ref, onMounted, inject } from 'vue'
import ChatPanel from './components/ChatPanel.vue'
import ConversationSidebar from './components/ConversationSidebar.vue'
import { ChatClientKey } from './infrastructure/chat-client'
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline'

const chatClient = inject(ChatClientKey)!
const selectedConversationId = ref<string | null>(null)
const selectedTitle = ref<string>('')
const refreshKey = ref(0)
const isSidebarOpen = ref(false)


const ensureInitialConversation = async () => {
  const list = await chatClient.listConversations()
  if (list.length === 0) {
    const c = await chatClient.createConversation()
    selectedConversationId.value = c.id
    selectedTitle.value = ''
  } else {
    selectedConversationId.value = list[0].id
    selectedTitle.value = list[0].title ?? ''
  }
}

onMounted(ensureInitialConversation)

const onSelect = (id: string, title: string) => {
  selectedConversationId.value = id
  selectedTitle.value = title
  isSidebarOpen.value = false
}

const onCreated = (id: string) => {
  selectedConversationId.value = id
  selectedTitle.value = ''
  isSidebarOpen.value = false
}

const onFirstResponse = async () => {
  if (!selectedConversationId.value) return
  const list = await chatClient.listConversations()
  const me = list.find(c => c.id === selectedConversationId.value)
  if (me) selectedTitle.value = me.title ?? selectedTitle.value
  refreshKey.value++
}

const toggleSidebar = () => (isSidebarOpen.value = !isSidebarOpen.value)
const closeSidebar = () => (isSidebarOpen.value = false)
</script>

<template>
  <div class="w-full h-full max-h-full overflow-hidden flex flex-col bg-gray-100 text-gray-700">
    <header class="relative w-full p-2 sm:p-4 bg-cyan-700 text-white">
      <!-- Mobile menu button -->
      <button
        class="md:hidden absolute left-2 top-1/2 -translate-y-1/2 p-2 rounded hover:bg-white/10 focus:outline-none"
        @click="toggleSidebar"
        aria-label="Toggle menu"
      >
        <Bars3Icon v-if="!isSidebarOpen" class="w-7 h-7" />
        <XMarkIcon v-else class="w-7 h-7" />
      </button>
      <h1 class="text-xl sm:text-2xl text-center">
        Chatbot Bob<span v-if="selectedTitle"> — {{ selectedTitle }}</span>
      </h1>
    </header>

    <main class="flex-1 flex overflow-hidden min-w-0">
      <!-- Desktop sidebar -->
      <aside class="hidden md:flex w-72 flex-shrink-0 border-r bg-white">
        <ConversationSidebar
          class="h-full w-full flex flex-col overflow-hidden"
          :selected-id="selectedConversationId || undefined"
          :refresh-key="refreshKey"
          @select="onSelect"
          @created="onCreated"
        />
      </aside>

      <!-- Mobile drawer -->
      <div class="fixed inset-0 z-50 md:hidden" v-show="isSidebarOpen">
        <div class="h-full w-full flex">
          <div
            class="w-5/6 h-full bg-white shadow-xl transform transition-transform duration-300 overflow-hidden"
            :class="isSidebarOpen ? 'translate-x-0' : '-translate-x-full'"
          >
            <ConversationSidebar
              class="h-full w-full flex flex-col overflow-hidden"
              :selected-id="selectedConversationId || undefined"
              :refresh-key="refreshKey"
              @select="onSelect"
              @created="onCreated"
            />
          </div>
          <div class="w-1/6 h-full bg-black/20" @click="closeSidebar"></div>
        </div>
      </div>

      <!-- Chat area  -->
      <section class="flex-1 min-w-0">
        <div class="h-full max-w-screen-md mx-auto p-2 sm:p-4 flex overflow-hidden min-w-0">
          <ChatPanel
            v-if="selectedConversationId"
            :conversation-id="selectedConversationId"
            @first-response="onFirstResponse"
          />
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped></style>
