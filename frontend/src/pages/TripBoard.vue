<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const d = ref(null)
onMounted(async () => { d.value = await getJSON('/api/dashboard') })
</script>
<template>
  <div class="page"><h1>行程板</h1>
    <p v-if="d">样例 {{ d.trip_count }} · 正常 {{ d.clean }} · 种子 {{ d.dirty }}</p>
  </div>
</template>
