<template>
  <div class="container">
    <div class="signform">
      <h2>비밀번호 재설정.</h2>
      <p>
        가입한 ID와 새로운 비밀번호를 입력하세요. <br>
        메일로 전달받은 확인 코드를 입력해주세요.
      </p>
      <div class="signform-inner">
        <input
          v-model="id"
          type="text"
          name="id"
          placeholder="id"
          @keyup.enter="reqFindPW"
          required
        >
        <br>
        <input
          v-model="pw"
          type="text"
          name="pw"
          placeholder="pw"
          @keyup.enter="reqFindPW"
          required
        >
        <br>
        <input
          v-model="code"
          type="text"
          name="code"
          placeholder="code"
          @keyup.enter="reqFindPW"
          required
        >
        <br>
        <button @click="reqFindPW">
          확 인
        </button>
      </div>
    </div>
    <div class="signform-help">
      <a href="/forgot">메일 재발송하기</a>
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
      code: null
    }
  },
  methods: {
    reqFindPW () {
      if (this.id === '' || this.id === null || this.pw === '' || this.pw === null || this.code === '' || this.code === null) {
        alert('모든 데이터를 입력해주세요.')
        return
      }

      const vm = this

      // Formdata 생성
      const form = new FormData()
      form.append('id', this.id.toLowerCase())
      form.append('pw', this.pw)
      form.append('confirmation_code', this.code)

      // Header
      const headers = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }

      // POST 요청
      const host = this.$store.getters.getHost
      const url = host + '/api/auth/resetpw'
      axios.post(url, form, headers)
        .then((res) => {
          alert('비밀번호가 변경되었습니다. 로그인 페이지로 이동합니다.')
          vm.$router.push('/signin')
        })
        .catch((error) => {
          console.log(error.response)
          if (error.response.status === 400) {
            alert(error.response.data.message)
          } else {
            alert('에러 발생!')
          }
        })
    }
  }
}
</script>
