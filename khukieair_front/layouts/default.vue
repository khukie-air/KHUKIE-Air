<template>
  <div>
    <div class="nav">
      <nuxt-link to="/">
        <img src="../assets/logo.png" height="85px">
      </nuxt-link>
    </div>
    <nuxt />
    <v-footer
      height="55"
      absolute
      class="font-weight-medium"
      dark
    >
      <v-col
        class="text-center"
        cols="12"
      >
        {{ new Date().getFullYear() }} — <strong>Khukie_air </strong><v-icon small>
          mdi-feather
        </v-icon>
      </v-col>
    </v-footer>
  </div>
</template>
