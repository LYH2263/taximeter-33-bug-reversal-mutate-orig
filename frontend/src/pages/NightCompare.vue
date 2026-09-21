<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const distance_km = ref(18)
const slow_min = ref(12)
const c = ref(null)
const run = async () => { c.value = await postJSON('/api/compare', { distance_km: distance_km.value, slow_min: slow_min.value, persist: true }) }
</script>
<template>
  <div class="page"><h1>昼夜对比</h1>
    <button @click="run">对比</button>
    <div v-if="c" class="panel">白天 ¥{{ c.day_total }} · 夜间 ¥{{ c.night_total }} · 差 ¥{{ c.delta }}</div>
  </div>
</template>
