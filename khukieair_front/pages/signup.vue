<template>
  <div class="container">
    <div class="signform">
      <h2>Sign up to KHUKIE</h2>
      <div class="signform-inner">
        <input
          v-model="id"
          type="text"
          name="id"
          placeholder="ID"
          @keyup.enter="reqSignup"
          required
        >
        <br>
        <input
          v-model="pw"
          type="password"
          name="password"
          placeholder="Password"
          @keyup.enter="reqSignup"
          required
        >
        <br>
        <input
          v-model="email"
          type="text"
          name="email"
          placeholder="E-mail"
          @keyup.enter="reqSignup"
          required
        >
        <br>
        <input
          v-model="name"
          type="text"
          name="name"
          placeholder="이름"
          @keyup.enter="reqSignup"
          required
        >
        <br>
        <button @click="reqSignup">
          가입
        </button>
      </div>
    </div>
    <div class="signform-help">
      <a href="/signin">기존 계정으로 로그인</a>
    </div>
    <div class="line" />
    <div class="OAuth">
      <button type="button" onclick="">
        <img src="~/assets/google.png">
        구글 계정으로 가입
      </button>
      <button type="button" onclick="">
        <img src="~/assets/kakao.png">
        카카오 계정으로 가입
      </button>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data: () => {
    return {
      id: null,
      pw: null,
      email: null,
      name: null
    }
  },
  methods: {
    reqSignup () {
      if (this.id === '' || this.id === null || this.pw === '' || this.pw === null ||
        this.email === '' || this.email === null || this.name === '' || this.name === null
      ) {
        alert('요구되는 데이터를 모두 입력해주세요.')
        return
      }

      const vm = this

      // Formdata 생성
      const form = new FormData()
      form.append('id', this.id.toLowerCase())
      form.append('pw', this.pw)
      form.append('email', this.email.toLowerCase())
      form.append('name', this.name)

      // Header
      const headers = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }

      // POST 요청
      const host = this.$store.getters.getHost
      const url = host + '/api/auth/signup'
      axios.post(url, form, headers)
        .then((res) => {
          alert('회원가입에 성공했습니다! 로그인 페이지로 이동합니다.')
          vm.$router.push('/signin')
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 400) {
            alert(error.response.data.message)
          } else {
            alert('회원가입 실패!')
          }
        })
    }
  }
}
</script>
