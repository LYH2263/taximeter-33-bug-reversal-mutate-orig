<script setup>
import { computed, onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'

const items = ref([])
const expanded = ref(new Set())
const highlight = ref(null)
const error = ref('')

// 每条记录的冲正表单状态，按 run id 索引
const forms = ref({})
const formOf = (id) => forms.value[id] || (forms.value[id] = { km: '', slow: '', preview: null, err: '', busy: false })

const byId = computed(() => new Map(items.value.map((x) => [x.id, x])))
const inList = (id) => id != null && byId.value.has(id)

const errText = (e) => {
  try { return JSON.parse(e.message).detail || e.message } catch { return e.message }
}

const load = async () => {
  items.value = (await getJSON('/api/history')).items
}
onMounted(load)

const toggle = (id) => {
  const next = new Set(expanded.value)
  next.has(id) ? next.delete(id) : next.add(id)
  expanded.value = next
}
const openRef = (id) => {
  if (!inList(id)) return
  const next = new Set(expanded.value)
  next.add(id)
  expanded.value = next
  highlight.value = id
}

const canReverse = (h) => h.kind === 'fare' && h.reversed_by == null

async function doPreview(h) {
  const f = formOf(h.id)
  f.err = ''
  error.value = ''
  try {
    f.preview = await postJSON(`/api/runs/${h.id}/reverse`, {
      distance_km: f.km === '' ? null : Number(f.km),
      slow_min: f.slow === '' ? null : Number(f.slow),
      preview: true,
    })
  } catch (e) { f.preview = null; f.err = errText(e) }
}

async function doCommit(h) {
  const f = formOf(h.id)
  f.err = ''
  error.value = ''
  f.busy = true
  try {
    const r = await postJSON(`/api/runs/${h.id}/reverse`, {
      distance_km: f.km === '' ? null : Number(f.km),
      slow_min: f.slow === '' ? null : Number(f.slow),
      preview: false,
    })
    f.km = ''; f.slow = ''; f.preview = null
    await load()
    // 同时展开原条与新条，引用关系立即可见
    expanded.value = new Set([...expanded.value, h.id, r.run_id])
    highlight.value = r.run_id
  } catch (e) {
    f.err = errText(e)
  } finally { f.busy = false }
}

const total = (h) => (h.kind === 'fare' ? h.result.total : `昼${h.result.day_total}/夜${h.result.night_total}`)
</script>
<template>
  <div class="page">
    <h1>记录</h1>
    <p v-if="error" class="err">{{ error }}</p>
    <table>
      <template v-for="h in items" :key="h.id">
        <tr :class="{ hl: highlight === h.id }">
          <td><a href="#" @click.prevent="toggle(h.id)">#{{ h.id }}</a></td>
          <td>{{ h.kind }}</td>
          <td>{{ h.input.distance_km }}km · {{ h.input.slow_min }}分<template v-if="h.input.night"> · 夜</template></td>
          <td>¥{{ total(h) }}</td>
          <td>
            <span v-if="h.reversed_by != null" class="tag tag-reversed">已被冲正
              <a v-if="inList(h.reversed_by)" href="#" @click.prevent="openRef(h.reversed_by)"> → #{{ h.reversed_by }}</a>
              <template v-else> → #{{ h.reversed_by }}</template>
            </span>
            <span v-else-if="h.reversal_of != null" class="tag tag-reversal">冲正自
              <a v-if="inList(h.reversal_of)" href="#" @click.prevent="openRef(h.reversal_of)"> #{{ h.reversal_of }}</a>
              <template v-else> #{{ h.reversal_of }}</template>
            </span>
          </td>
        </tr>
        <tr v-if="expanded.has(h.id)">
          <td colspan="5" class="detail">
            <div class="panel">
              <p v-if="h.kind === 'fare'">
                起步 {{ h.result.start }} · 里程 {{ h.result.mileage }} · 低速 {{ h.result.slow_fee }} ·
                <strong>合计 ¥{{ h.result.total }}</strong><template v-if="h.result.night">（夜间 ×{{ h.result.night_factor }}）</template>
              </p>
              <p v-else>
                白天 ¥{{ h.result.day_total }} · 夜间 ¥{{ h.result.night_total }} · 差额 ¥{{ h.result.delta }}
              </p>

              <template v-if="canReverse(h)">
                <div class="reverse-form">
                  <strong>冲正</strong>
                  <label>新公里 <input type="number" min="0" v-model="formOf(h.id).km" /></label>
                  <label>新低速 <input type="number" min="0" v-model="formOf(h.id).slow" /></label>
                  <button @click="doPreview(h)">预览</button>
                  <button @click="doCommit(h)" :disabled="formOf(h.id).busy">提交冲正</button>
                  <span v-if="formOf(h.id).err" class="err">{{ formOf(h.id).err }}</span>
                </div>
                <div v-if="formOf(h.id).preview" class="preview">
                  预览（不落库）：起步 {{ formOf(h.id).preview.start }} · 里程 {{ formOf(h.id).preview.mileage }}
                  · 低速 {{ formOf(h.id).preview.slow_fee }} · <strong>合计 ¥{{ formOf(h.id).preview.total }}</strong>
                </div>
              </template>
              <p v-else-if="h.kind === 'compare'" class="muted">compare 记录不能冲正</p>
              <p v-else-if="h.reversed_by != null" class="muted">该记录已被冲正，不能再次冲正；原拆解保留不改写</p>
            </div>
          </td>
        </tr>
      </template>
    </table>
  </div>
</template>
<style scoped>
.tag { font-size:0.8rem; padding:0.1rem 0.4rem; border-radius:4px; }
.tag-reversed { background:#5a2a1a; color:#ffb09a; }
.tag-reversal { background:#244a2a; color:#9be8ac; }
.detail { background:#221a0c; }
.reverse-form { display:flex; gap:0.6rem; align-items:center; flex-wrap:wrap; margin-top:0.5rem; }
.preview { margin-top:0.4rem; color:var(--accent); }
.err { color:#ff8a6a; }
.muted { color:var(--muted); }
tr.hl td { outline:2px solid var(--accent); }
</style>
