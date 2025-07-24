import type { Message } from '@/domain/message'
import { type AxiosInstance } from 'axios'
import { type InjectionKey } from 'vue'

type MessageHistoryResponse = {
  messages: Message[]
}

type MessageRequest = {
  content: string
}

export class ChatClient {
  constructor(private httpClient: AxiosInstance) {}

  async getMessageHistory(): Promise<Message[]> {
    const resp = await this.httpClient.get<MessageHistoryResponse>('/chat/messages')
    return resp.data.messages
  }

  async sendMessage(content: string): Promise<void> {
    await this.httpClient.post('/chat/messages', { content } as MessageRequest)
  }

  async subscribe(messageCallback: (message: Message) => void) {
    const reconnectInterval = 1000
    let ws: WebSocket | undefined

    const connect = () => {
      ws = new WebSocket('/api/chat/notifications')
      ws.onopen = () => {
        console.log('Websocket connection established.')
      }
      ws.onmessage = (e: MessageEvent) => {
        const message = JSON.parse(e.data) as Message
        messageCallback(message)
      }
      ws.onclose = (e: CloseEvent) => {
        console.log(
          `Websocket connection was closed, attempting to reconnect in ${reconnectInterval}ms.`,
        )
        setTimeout(connect, reconnectInterval)
      }
    }

    connect()
  }
}

export const ChatClientKey = Symbol('ChatClient') as InjectionKey<ChatClient>
