<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const t = ref(null)
onMounted(async () => { t.value = await getJSON('/api/tariff') })
</script>
<template>
  <div class="page"><h1>运价表</h1><pre v-if="t">{{ t }}</pre></div>
</template>
