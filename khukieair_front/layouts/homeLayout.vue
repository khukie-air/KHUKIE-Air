<template>
  <v-app light>
    <v-navigation-drawer
      app
      absolute
      permanent
      right
      color="brown darken-2"
      width="180px"
    >
      <template v-slot:prepend>
        <v-list-item three-line />
        <v-list-item three-line>
          <nuxt-link to="/edit/">
            <v-list-item-avatar>
              <img src="../assets/monster.png">
            </v-list-item-avatar>
          </nuxt-link>
          <v-list-item-content>
            <v-list-item-title>{{ user.name }} 님</v-list-item-title>
            <v-list-item-subtitle>{{ user.id }}</v-list-item-subtitle>
            <v-list-item-subtitle>
              <a @click="signout">
                Sign out
              </a>
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </template>
      <v-divider class="mx-4" />
      <!-- <v-card-actions>
        <v-btn small color="brown" @click.stop="dialog = true">
          <v-icon left small>
            mdi-file-upload
          </v-icon> File Upload <v-icon color="brown" small>
            file
          </v-icon>
        </v-btn>
      </v-card-actions> -->

      <!-- File upload modal -->
      <!-- <v-dialog v-model="dialog" max-width="700">
        <v-card color="brown">
          <v-card-actions>
            <v-file-input
              small-chips
              v-model="fileInput"
              label="File Upload"
              refs="fileInput"
            />
            <v-spacer />
            <v-btn text @click="fileUpload">
              Upload
            </v-btn>
            <v-btn text @click="closeFileDialog">
              cancel
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog> -->

      <v-divider class="mx-4" />
      <v-card-actions>
        <v-btn color="brown" small>
          <v-icon left medium>
            mdi-account-arrow-right
          </v-icon>
          Delete  Account
        </v-btn>
      </v-card-actions>
      <v-card-actions>
        <v-btn color="brown" small @click="goTrashBox">
          <v-icon left medium>
            mdi-delete-variant
          </v-icon>
          Go TrashBox
        </v-btn>
      </v-card-actions>
    </v-navigation-drawer>
    <v-app-bar
      app
      clipped-right
      color="brown darken-4"
      height="90"
    >
      <v-col
        class="text-center"
        cols="12"
      >
        <nuxt-link to="/home/">
          <img src="../assets/logo.png" height="85px">
        </nuxt-link>
      </v-col>
    </v-app-bar>

    <v-content>
      <v-container>
        <nuxt /> <!-- 이부분이 핵심 index.vue가 보여지는 부분이다. -->
      </v-container>
    </v-content>

    <v-footer
      height="55"
      absolute
    >
      <v-col>
        {{ new Date().getFullYear() }}
        —
        <v-icon small color="brown lighten-2">
          mdi-cookie
        </v-icon>
        Khukie_air
        <v-icon small>
          mdi-feather
        </v-icon>
      </v-col>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  data () {
    return {
      items: [
      ],
      user: {
        name: '',
        id: '',
        email: ''
      }
    }
  },
  mounted () {
    this.loadUserData()
  },
  methods: {
    signout () {
      this.$store.dispatch('LOGOUT')
      alert('로그아웃 되었습니다!')
      this.$router.push('/signin')
    },
    loadUserData () {
      // 로그인된 유저 데이터
      const user = this.$store.getters.getUserInfo
      this.user.name = user.name
      this.user.id = user.id
      this.user.email = user.email
    },
    goTrashBox () {
      this.$router.push('/home/trashbox')
    }
  }
}
</script>
