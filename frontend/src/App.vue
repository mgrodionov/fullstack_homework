<template>
  <router-view v-slot="{ Component }">
    <div>
      <transition name="router-fade">
        <component :is="Component" />
      </transition>
    </div>
  </router-view>
</template>


<style scoped>
.router-fade-enter-active,
.router-fade-leave-active {
  transition: opacity 0.4s ease-in-out;
}

.router-fade-enter-from,
.router-fade-leave-to {
  opacity: 0;
}
</style>