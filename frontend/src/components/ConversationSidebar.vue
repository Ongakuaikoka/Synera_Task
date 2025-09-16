<script setup lang="ts">
import { inject, onMounted, ref, watch } from 'vue'
import type { ConversationSummary } from '@/domain/conversation'
import { ChatClientKey } from '@/infrastructure/chat-client'

const chatClient = inject(ChatClientKey)!

const props = defineProps<{
  selectedId?: string
  refreshKey?: number
}>()

const emit = defineEmits<{
  select: [id: string, title: string]
  created: [id: string]
}>()

const conversations = ref<ConversationSummary[]>([])

const refresh = async () => {
  const all = await chatClient.listConversations()
  conversations.value = all.filter(c => (c.title ?? '').trim().length > 0)
}

const onSelect = (c: ConversationSummary) => {
  emit('select', c.id, c.title.trim())
}

const onCreate = async () => {
  const c = await chatClient.createConversation()
  emit('created', c.id)
}

onMounted(refresh)
watch(() => props.refreshKey, refresh)
</script>


<template>
  <div class="h-full w-full flex flex-col overflow-hidden">
    <!-- Top bar -->
    <div class="p-3 border-b flex-shrink-0">
      <button
        class="w-full bg-emerald-500 hover:bg-emerald-400 text-white rounded-lg py-2 px-3 font-medium"
        @click="onCreate"
      >
        New Conversation
      </button>
    </div>

    <!-- Conversations list -->
    <div class="flex-1 overflow-y-auto">
        <ul v-if="conversations.length" class="py-2 space-y-1">
            <li v-for="c in conversations" :key="c.id">
                <button
                class="w-full text-left px-3 py-2 rounded-lg border transition
                        hover:bg-cyan-50 hover:border-cyan-200"
                :class="c.id === selectedId ? 'bg-cyan-50 border-cyan-300' : 'bg-white border-transparent'"
                @click="onSelect(c)"
                >
                <div class="flex items-center gap-2">
                    <div class="min-w-0 flex-1">
                    <div class="text-sm font-medium truncate">
                        {{ c.title || 'Awaiting first reply…' }}
                    </div>
                    <div class="text-xs text-gray-400 truncate">
                        {{ new Date(c.last_activity_at || c.created_at).toLocaleString() }}
                    </div>
                    </div>
                </div>
                </button>
            </li>
        </ul>

      <div v-else class="p-4 text-sm text-gray-500">
        No conversations yet. Start a new one!
      </div>
    </div>
  </div>
</template>

