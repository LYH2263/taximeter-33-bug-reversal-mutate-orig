<template>
  <div class="taxi-layout">
    <div class="meter-dial">
      <div class="dial-face">计价</div>
      <nav>
        <router-link to="/">行程板</router-link>
        <router-link to="/trips">列表</router-link>
        <router-link to="/meter">打表</router-link>
        <router-link to="/tariff">运价</router-link>
        <router-link to="/night">昼夜对比</router-link>
        <router-link to="/history">记录</router-link>
        <router-link to="/settings">设置</router-link>
      </nav>
    </div>
    <section class="content"><router-view /></section>
  </div>
</template>
