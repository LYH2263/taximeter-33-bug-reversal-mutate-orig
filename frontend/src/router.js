import { createRouter, createWebHistory } from 'vue-router'
import TripBoard from './pages/TripBoard.vue'
import TripList from './pages/TripList.vue'
import TripDetail from './pages/TripDetail.vue'
import FareMeter from './pages/FareMeter.vue'
import TariffRules from './pages/TariffRules.vue'
import NightCompare from './pages/NightCompare.vue'
import RunHistory from './pages/RunHistory.vue'
import Settings from './pages/Settings.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: TripBoard },
    { path: '/trips', component: TripList },
    { path: '/trips/:id', component: TripDetail },
    { path: '/meter', component: FareMeter },
    { path: '/tariff', component: TariffRules },
    { path: '/night', component: NightCompare },
    { path: '/history', component: RunHistory },
    { path: '/settings', component: Settings },
  ],
})
