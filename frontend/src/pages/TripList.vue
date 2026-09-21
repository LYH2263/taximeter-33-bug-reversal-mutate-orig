<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
onMounted(async () => { items.value = (await getJSON('/api/trips')).items })
</script>
<template>
  <div class="page"><h1>行程</h1>
    <table><tr v-for="t in items" :key="t.id"><td>{{ t.label }}</td><td>{{ t.distance_km }}km</td>
      <td><router-link :to="`/trips/${t.id}`">详情</router-link></td></tr></table>
  </div>
</template>
