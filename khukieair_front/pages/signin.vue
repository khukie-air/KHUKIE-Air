<template>
  <div class="container">
    <div class="signform">
      <h2>Sign in to KHUKIE</h2>
      <div class="signform-inner">
        <input v-model="id" type="text" name="id" placeholder="E-mail" @keyup.enter="reqLogin">
        <br>
        <input v-model="pw" type="password" name="password" placeholder="Password" @keyup.enter="reqLogin">
        <br>
        <button @click="reqLogin">
          로그인
        </button>
      </div>
    </div>
    <div class="signform-help">
      <a href="/forgot">비밀번호를 잊으셨나요?</a>
      &nbsp;•&nbsp;
      <a href="/signup">계정 만들기</a>
    </div>
    <div class="line" />
    <div class="OAuth">
      <button type="button" onclick="">
        <img src="~/assets/google.png">
        구글 계정으로 로그인
      </button>
      <button type="button" onclick="">
        <img src="~/assets/kakao.png">
        카카오 계정으로 로그인
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data: () => {
    return {
      id: null,
      pw: null
    }
  },
  created () {
    this.$store.dispatch('LOGOUT')
  },
  methods: {
    reqLogin () {
      if (this.id === '' || this.id === null || this.pw === '' || this.pw === null) {
        alert('아이디와 비밀번호를 모두 입력해주세요.')
        return
      }

      const vm = this
      const id = this.id.toLowerCase()
      const pw = this.pw
      this.$store
        .dispatch('LOGIN', { id, pw })
        .then(() => {
          vm.$router.push('/home')
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 401) {
            alert('아이디 혹은 비밀번호가 잘못되었습니다.')
          } else {
            alert('로그인 실패!')
          }
        })
    }
  }
}
</script>
