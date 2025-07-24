<script setup lang="ts">
import ChatPanel from './components/ChatPanel.vue'
</script>

<template>
  <div class="w-full h-full max-h-full overflow-hidden flex flex-col bg-gray-100 text-gray-700">
    <header class="w-full p-2 sm:p-4 bg-cyan-700 text-white text-xl sm:text-2xl text-center">
      <h1>Chatbot Bob</h1>
    </header>
    <main class="flex-1 w-full max-w-screen-md mx-auto p-2 sm:p-4 flex overflow-hidden min-w-0">
      <ChatPanel />
    </main>
  </div>
</template>

<style scoped></style>
