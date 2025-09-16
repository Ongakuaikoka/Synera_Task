import type { Message } from '@/domain/message'
import type { ConversationSummary } from '@/domain/conversation'
import { type AxiosInstance } from 'axios'
import { type InjectionKey } from 'vue'

type MessageHistoryResponse = { messages: Message[] }
type MessageRequest = { content: string }

type ConversationsResponse = { conversations: ConversationSummary[] }
type ConversationCreateResponse = { id: string; title?: string | null }

export class ChatClient {
  constructor(private httpClient: AxiosInstance) {}

  async createConversation(): Promise<ConversationSummary> {
    const resp = await this.httpClient.post<ConversationCreateResponse>('/chat/conversations')
    return { id: resp.data.id, created_at: new Date().toISOString(), title: resp.data.title ?? null }
  }

  async listConversations(): Promise<ConversationSummary[]> {
    const resp = await this.httpClient.get<ConversationsResponse>('/chat/conversations')
    return resp.data.conversations
  }

  async getConversationHistory(conversationId: string): Promise<Message[]> {
    const resp = await this.httpClient.get<MessageHistoryResponse>(
      `/chat/conversations/${conversationId}/messages`,
    )
    return resp.data.messages
  }

  async sendConversationMessage(conversationId: string, content: string): Promise<void> {
    await this.httpClient.post(`/chat/conversations/${conversationId}/messages`, { content } as MessageRequest)
  }

  subscribe(
    conversationId: string,
    messageCallback: (message: Message) => void
  ): () => void {
    let ws: WebSocket | undefined
    let reconnectTimer: number | undefined
    let shouldReconnect = true
    const RECONNECT_MS = 1000
  
    const wsUrl = () => {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws'
      return `${proto}://${location.host}/api/chat/conversations/${conversationId}/notifications`
    }
  
    const connect = () => {
      if (!shouldReconnect) return
  
      ws = new WebSocket(wsUrl())
  
      ws.onmessage = (e: MessageEvent<string>) => {
        messageCallback(JSON.parse(e.data) as Message)
      }
    
      ws.onclose = () => {
        if (!shouldReconnect) return
        reconnectTimer = window.setTimeout(connect, RECONNECT_MS)
      }
    }
  
    connect()
  
    return () => {
      shouldReconnect = false
      if (reconnectTimer) window.clearTimeout(reconnectTimer)
      if (!ws) return
  
      if (ws.readyState === WebSocket.CONNECTING) {
        const handler = () => {
          ws?.removeEventListener('open', handler)
          ws?.close()
        }
        ws.addEventListener('open', handler)
      } else {
        ws.close()
      }
    }
  }
  
}

export const ChatClientKey = Symbol('ChatClient') as InjectionKey<ChatClient>
