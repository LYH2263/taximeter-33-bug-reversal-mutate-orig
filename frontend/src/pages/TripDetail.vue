<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
const route = useRoute()
const trip = ref(null)
const fare = ref(null)
const load = async () => {
  trip.value = await getJSON(`/api/trips/${route.params.id}`)
  fare.value = await postJSON('/api/fare', { distance_km: trip.value.distance_km, slow_min: trip.value.slow_min, night: !!trip.value.night, trip_id: trip.value.id, persist: false })
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template>
  <div class="page" v-if="trip"><h1>{{ trip.label }}</h1>
    <p class="hero-num">¥{{ fare?.total }}</p>
    <p>起步 {{ fare?.start }} · 里程 {{ fare?.mileage }} · 低速 {{ fare?.slow_fee }}</p>
  </div>
</template>
